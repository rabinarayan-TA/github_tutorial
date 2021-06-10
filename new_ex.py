def get_decile_profiles(
    context,
    run_id,
    index_cols=["pop_cust_id"],
    remove_any=["target_ecom_ltv", "target_digital_ltv"],
    use_cols_features=["features", "importances"],
    placeholders=[
        "Use case",
        "Segment",
        "Train & Test efforts",
        "Valid efforts",
        "Train auc",
        "Test auc",
        "Valid auc",
        "Train SMAPE",
        "Test SMAPE",
        "Valid SMAPE",
    ],
):

    usecase = context.config["model_results"]["use_case"]
    run_id_1 = context.config["model_results"]["target_var_run_id"]
    run_id_2 = context.config["model_results"]["multiplicative_target_run_id"]
    metric_col = context.config["model_results"]["target_var"]
    target_cols = context.config["model_dev"]["target_usecase"]

    list_df = {}
    list_df.update({"placeholders": placeholders})
    writer = pd.ExcelWriter(f"profiling_{run_id}.xlsx", engine="xlsxwriter")
    workbook = writer.book

    ## create required excel formatting objects
    list_df = get_excel_format(context, list_df, workbook)

    # read models
    gcs = gcsfs.GCSFileSystem()
    ## update the model names
    model_path = f"gs://bkt_tigeranalytics_artifacts_repository/mlflow/dev/{run_id_1}/artifacts/model_objects/model_{run_id_1}.joblib"
    with gcs.open(model_path, "rb") as fp:
        model_target_var = joblib.load(fp)
    list_df.update(
        {
            metric_col.replace("_yhat", "_model"): re.sub(
                "\s+", "", str(model_target_var).replace("\n", "")
            )
        }
    )
    list_df.update({"metric_col": metric_col})

    if context.config["model_results"]["multiplicative_model"]:
        target_name = context.config["model_results"]["multiplicative_target"]
        list_df.update({"multiplicative_target": target_name})
        model_path = f"gs://bkt_tigeranalytics_artifacts_repository/mlflow/dev/{run_id_2}/artifacts/model_objects/model_{run_id_2}.joblib"
        with gcs.open(model_path, "rb") as fp:
            model_multiplicative_target_var = joblib.load(fp)
        list_df.update(
            {
                target_name.replace("_yhat", "_model"): re.sub(
                    "\s+", "", str(model_multiplicative_target_var).replace("\n", "")
                )
            }
        )

    #### Read the scores
    df_scores = pd.read_parquet(
        f"gs://bkt_tigeranalytics_artifacts_repository/mlflow/dev/{run_id_1}/artifacts/data/valid_data_{run_id_1}.parquet"
    )
    df_scores = df_scores[index_cols + [metric_col] + target_cols]

    ##### Read multiplicative model scores
    if context.config["model_results"]["multiplicative_model"]:
        multiplicative_target = context.config["model_results"]["multiplicative_target"]
        multiplicative_scores = pd.read_parquet(
            f"gs://bkt_tigeranalytics_artifacts_repository/mlflow/dev/{run_id_2}/artifacts/data/valid_data_{run_id_2}.parquet"
        )
        multiplicative_scores = multiplicative_scores[
            index_cols + [multiplicative_target]
        ]
        df_scores = df_scores.merge(
            multiplicative_scores, on=index_cols, validate="1:1"
        )
        df_scores["multiplied_score"] = (
            df_scores[f"{metric_col}"] * df_scores[f"{multiplicative_target}"]
        )

    df_scores[target_cols] = df_scores[target_cols].fillna(0)

    if usecase == "uc6_postcards":
        if context.config["model_results"]["bins"]:
            bin_column = context.config["model_results"]["bins"]["column"]
            bin_values = context.config["model_results"]["bins"]["bin_values"]
            df_scores["binned_col"] = pd.cut(df_scores[bin_column], bin_values)

    if context.config["model_results"]["multiplicative_model"]:
        required_cols = context.config["model_results"]["scoring_cols_report"] + [
            "multiplied_score"
        ]
    else:
        required_cols = context.config["model_results"]["scoring_cols_report"]

    ##### create Profiles for different targets like opt, ltv and multiplied model
    for score_col in required_cols:
        df_profile = pch_gains(
            context,
            df_input=df_scores,
            score_col=score_col,
            cut_off_points=deciles_,
            treat_outliers=False,
            train=False,
        )
        df_profile = profile_format(df_profile, score_col)
        df_scores[f"{score_col.replace('target_','')}_deciles"] = pd.qcut(
            df_scores[score_col].rank(method="first"), 10, labels=list(range(1, 11))
        ).astype(int)
        list_df.update({df_profile.name: df_profile})

    ##### create decile by decile 10 x 10 matrix for population
    if context.config["model_results"]["multiplicative_model"]:
        population_by_deciles = (
            pd.crosstab(
                df_scores[f"{metric_col.replace('target_','')}_deciles"],
                df_scores[f"multiplied_score_deciles"],
            )
            .sort_index(axis=1, level=1, ascending=False)
            .sort_index(axis=0, ascending=False)
        )
        population_by_deciles.columns = population_by_deciles.columns.astype(str)
        population_by_deciles = population_by_deciles.reset_index()
        population_by_deciles.columns.name = f"multiplied_score"
        population_by_deciles.name = "Population by deciles"
        list_df.update({population_by_deciles.name: population_by_deciles})

        target_cols = list(set(target_cols).difference(remove_any))

        ##### create decile by decile 10 x 10 matrix for different targets like opt and ltv
        for actuals in target_cols:
            df_by_deciles = (
                df_scores.pivot_table(
                    index=f"{metric_col.replace('target_','')}_deciles",
                    columns=f"multiplied_score_deciles",
                    values=actuals,
                    aggfunc="mean",
                    fill_value=0,
                )
                .sort_index(axis=1, level=1, ascending=False)
                .sort_index(axis=0, ascending=False)
            )
            df_by_deciles.columns = df_by_deciles.columns.astype(str)
            df_by_deciles = df_by_deciles.reset_index()
            df_by_deciles = df_by_deciles.round(3)
            df_by_deciles.columns.name = f"multiplied_score"
            df_by_deciles.name = f"{actuals.replace('target_','')} by deciles"
            list_df.update({df_by_deciles.name: df_by_deciles})

    #     if usecase = "uc8_email_orders":
    #         for col in context.config["model_results"]['lift_tables_target']:
    #             df_scores[f"{col.replace('target_','')}_deciles"]= pd.qcut(df_scores[score_col].rank(method = 'first'),10,labels=list(range(1,11))).astype(int)
    #             population_by_deciles = pd.crosstab(df_scores[f"{metric_col.replace('target_','')}_deciles"],df_scores[f"{col.replace('target_','')}_deciles"]).sort_index(axis=1, level=1,ascending = False).sort_index(axis=0,ascending = False)
    #             population_by_deciles.columns = population_by_deciles.columns.astype(str)
    #             population_by_deciles = population_by_deciles.reset_index()
    #             population_by_deciles.columns.name = 'target by deciles'
    #             population_by_deciles.name = 'predicted target by deciles'
    #             list_df.update({population_by_deciles.name:population_by_deciles})

    ##### create profiles for train
    if context.config["model_results"]["include_train"]:
        if usecase == "uc6_postcards":
            for score_col in required_cols:
                print(score_col)
                if "multiplied_score" not in score_col:
                    if "opt" in score_col:
                        ltv = False
                        run_id = run_id_1
                    elif "ltv" in score_col:
                        ltv = True
                        run_id = run_id_2

                    train_scores = pd.read_parquet(
                        f"gs://bkt_tigeranalytics_artifacts_repository/mlflow/dev/{run_id}/artifacts/data/train_data_{run_id}.parquet"
                    )
                    if "ltv" in score_col:
                        df_train = load_dataset(context, "train_test_uc6")
                        train_scores = train_scores.merge(
                            df_train[
                                ["pop_cust_id", "target_digital_ltv", "target_ecom_ltv"]
                            ],
                            on=["pop_cust_id"],
                        )
                    bin_column = context.config["model_results"]["bins"]["column"]
                    bin_values = context.config["model_results"]["bins"]["bin_values"]
                    train_scores["binned_col"] = pd.cut(
                        train_scores[bin_column], bin_values
                    )
                    df_profile = pch_gains(
                        context,
                        df_input=train_scores,
                        score_col=score_col,
                        cut_off_points=deciles_,
                        treat_outliers=False,
                        ltv=ltv,
                        train=True,
                    )
                    df_profile = profile_format(df_profile, score_col=score_col)
                    train_scores[
                        f"{score_col.replace('target_','')}_deciles"
                    ] = pd.qcut(
                        train_scores[score_col].rank(method="first"),
                        10,
                        labels=list(range(1, 11)),
                    ).astype(
                        int
                    )
                    list_df.update({df_profile.name + "_train": df_profile})
        else:
            for score_col in required_cols:
                print(score_col)
                ltv = False
                run_id = run_id_1
                train_scores = pd.read_parquet(
                    f"gs://bkt_tigeranalytics_artifacts_repository/mlflow/dev/{run_id}/artifacts/data/train_data_{run_id}.parquet"
                )
                train_scores[target_cols] = train_scores[target_cols].fillna(0)
                df_profile = pch_gains(
                    context,
                    df_input=train_scores,
                    score_col=score_col,
                    cut_off_points=deciles_,
                    treat_outliers=False,
                    ltv=ltv,
                    train=True,
                )
                df_profile = profile_format(df_profile, score_col=score_col)
                train_scores[f"{score_col.replace('target_','')}_deciles"] = pd.qcut(
                    train_scores[score_col].rank(method="first"),
                    10,
                    labels=list(range(1, 11)),
                ).astype(int)
                list_df.update({df_profile.name + "_train": df_profile})

    ##### create profiles for test
    if context.config["model_results"]["include_test"]:
        if usecase == "uc6_postcards":
            for score_col in required_cols:
                print(score_col)
                if "multiplied_score" not in score_col:
                    if "opt" in score_col:
                        ltv = False
                        run_id = run_id_1
                    elif "ltv" in score_col:
                        ltv = True
                        run_id = run_id_2
                    test_scores = pd.read_parquet(
                        f"gs://bkt_tigeranalytics_artifacts_repository/mlflow/dev/{run_id}/artifacts/data/test_data_{run_id}.parquet"
                    )
                    if "ltv" in score_col:
                        df_test = load_dataset(context, "train_test_uc6")
                        test_scores = test_scores.merge(
                            df_test[
                                ["pop_cust_id", "target_digital_ltv", "target_ecom_ltv"]
                            ],
                            on=["pop_cust_id"],
                        )
                    bin_column = context.config["model_results"]["bins"]["column"]
                    bin_values = context.config["model_results"]["bins"]["bin_values"]
                    test_scores["binned_col"] = pd.cut(
                        test_scores[bin_column], bin_values
                    )
                    df_profile = pch_gains(
                        context,
                        df_input=test_scores,
                        score_col=score_col,
                        cut_off_points=deciles_,
                        treat_outliers=False,
                        ltv=ltv,
                        train=True,
                    )
                    df_profile = profile_format(df_profile, score_col)
                    test_scores[f"{score_col.replace('target_','')}_deciles"] = pd.qcut(
                        test_scores[score_col].rank(method="first"),
                        10,
                        labels=list(range(1, 11)),
                    ).astype(int)
                    list_df.update({df_profile.name + "_test": df_profile})

        else:
            for score_col in required_cols:
                print(score_col)
                ltv = False
                run_id = run_id_1
                test_scores = pd.read_parquet(
                    f"gs://bkt_tigeranalytics_artifacts_repository/mlflow/dev/{run_id}/artifacts/data/test_data_{run_id}.parquet"
                )
                test_scores[target_cols] = test_scores[target_cols].fillna(0)
                df_profile = pch_gains(
                    context,
                    df_input=test_scores,
                    score_col=score_col,
                    cut_off_points=deciles_,
                    treat_outliers=False,
                    ltv=ltv,
                    train=True,
                )
                df_profile = profile_format(df_profile, score_col)
                test_scores[f"{score_col.replace('target_','')}_deciles"] = pd.qcut(
                    test_scores[score_col].rank(method="first"),
                    10,
                    labels=list(range(1, 11)),
                ).astype(int)
                list_df.update({df_profile.name + "_test": df_profile})

    ### report generation
    generate_report(writer=writer, workbook=workbook, list_df=list_df)

    # write feature importances

    write_feature_importances(
        context=context,
        run_id=run_id_1,
        use_cols_features=use_cols_features,
        writer=writer,
        workbook=workbook,
        target=metric_col,
    )

    if context.config["model_results"]["multiplicative_model"]:
        write_feature_importances(
            context=context,
            run_id=run_id_2,
            use_cols_features=use_cols_features,
            writer=writer,
            workbook=workbook,
            target=multiplicative_target,
        )

    # correlations
    write_correlation_matrix(
        run_id=run_id_1, target=metric_col, writer=writer, workbook=workbook
    )

    if context.config["model_results"]["multiplicative_model"]:
        write_correlation_matrix(
            run_id=run_id_2,
            target=multiplicative_target,
            writer=writer,
            workbook=workbook,
        )

    writer.save()
    return
