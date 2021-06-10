def lift_tables(pch_ta_validation,col_, col, cut_off_points, target="ord_resp", add_counts=True,):
    df=pch_ta_validation.copy()
    df.rename(columns={col_:'target',col:'yhat'},inplace=True)
#     df = pd.DataFrame()
#     df["target"] = y.copy()
#     df["yhat"] = yhat.copy()
    df.sort_values('yhat', ascending=False, inplace=True)
    labels = [str(round(d * 100)) + "%" for d in cut_off_points]
    out_df = pd.DataFrame(
        {
            "Bucket": labels,
            f"{target}_mean": 0,
            f"{target}_lift": 0,
        }
    )
    if add_counts:
        out_df['pop_size'] = 0
    avg_y = df['target'].sum()/len(df['target'])
    prev_bucket = 0
    for i, decile in enumerate(cut_off_points):
        top_df = df.iloc[prev_bucket: int(decile * len(df))]
        out_df.loc[i, f"{target}_mean"] = top_df.target.sum()/len(top_df)
        top_df = df.iloc[: int(decile * len(df))]
        out_df.loc[i, f"{target}_cum_mean"] = top_df.target.sum()/len(top_df)
        if add_counts:
            out_df.loc[i,'pop_size'] = len(top_df)
        prev_bucket = int(decile * len(df))
    out_df[f"{target}_lift"] = out_df[f"{target}_cum_mean"] / avg_y
    return out_df



