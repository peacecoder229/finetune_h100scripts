#!/usr/bin/env python3
import argparse
import pandas as pd
import sys
import json
import re

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process CSV files with various options.")
    parser.add_argument("--applyrulefirst", action="store_true", help="Apply rules before other operations. If not set, rules will be applied after other operations if specified.")
    parser.add_argument("--inputfile", help="Input file name. Example usage: --inputfile 'data.csv'")
    parser.add_argument("--outputfile", help="Output file name. Example usage: --outputfile 'processed_data.csv'")
    parser.add_argument("--rule", help="Provide string with rule on cols of CSV like: --rule \"'hpcores': == 16,&,'hpdelay': == 0,&,'lpcores': == 16\"")
    parser.add_argument("--sortby", help="Provide JSON string to sort by column names and order like: --sortby '{\"column1\": true, \"column2\": false}'")
    parser.add_argument("--newcol", help="Add a new column with an operation on existing columns. Example usage: --newcol 'newcolname: df.hpcores + df.lpcores'")
    parser.add_argument("--aggregatecolumns", help="Aggregate column operations. Example usage: --aggregatecolumns \"'avg_temp': 'temp_[0-9]': 'mean'\"")
    parser.add_argument("--multifile", help="Operations for multiple files. Example usage: --multifile \"file1.csv,file2.csv: 'new_col'; '100 * (df1.col1 - df2.col1) / df1.col1'\"")
    parser.add_argument("--addcol", help="Add new calculated columns. Example usage: --addcol \"'newcol1': 'df[\"col1\"] * (1 - df[\"col2\"])', 'newcol2': 'df[\"col3\"] / df[\"col4\"]'\"")
    parser.add_argument("--sortcol", help="JSON string to sort by multiple columns and orders. Example usage: --sortcol '{\"revenue\": \"desc\", \"date\": \"asc\"}'")
    parser.add_argument("--extraprintcols", help="List of extra columns to print. Example usage: --extraprintcols 'col1,col2,col3'", default=None)
    parser.add_argument("--topn", type=int, default=5, help="Number of top values to print. Default is 5. Example usage: --topn 5")
    parser.add_argument("--printcol", help="Column whose top N values to print after sorting. If not specified, the first sorted column is used. Example usage: --printcol 'profit'")
    return parser.parse_args()

def read_and_clean_csv(filename):
    # Read CSV file
    df = pd.read_csv(filename, sep=",", header=0)
    dforig = df.copy()
    # Function to simplify kernel names
    def clean_kernel_name(name):
        # Adjusted regex to stop at the first occurrence of '<' or '(' after capturing the kernel name
        match = re.search(r"tensorrt_llm::kernels::([^\s:<>\(]+)", name)
        if match:
            return match.group(1)  # Return only the function name
        return name  # Return the original name if no patterns match

    # Apply the cleaning function to the 'Kernel Name' column
    df['Kernel Name'] = df['Kernel Name'].apply(clean_kernel_name)

    return df, dforig


def read_csv(filename):
    return pd.read_csv(filename, sep=",", header=0)

def add_new_columns(df, newcol_definitions):
    if newcol_definitions:
        col_name, operation = newcol_definitions.split(":")
        df[col_name.strip()] = pd.eval(operation.strip())

def apply_sorting(df, sortkeys_json):
    if sortkeys_json:
        sortkeys = json.loads(sortkeys_json)
        sort_cols = list(sortkeys.keys())
        #ascending_list = list(sortkeys.values())
        ascending_list = [sortkeys[col] == 'asc' for col in sort_cols]  # Convert to boolean
        df.sort_values(by=sort_cols, ascending=ascending_list, inplace=True)



def apply_rules(df, rules):
    if rules:
        #df['Kernel Name'] = df['Kernel Name'].str.strip()
        #print("Exact match check for debug:")
        #print(df[df['Kernel Name'] == 'sm90_xmma_gemm_f16f16_f16f32_f32_tn_n_tilesize256x128x64'])
# Then apply contains

        flt = ""
        rules_list = rules.split(",")
        for i in rules_list:
            if i.strip() in ['&', '|']:
                flt += f" {i.strip()} "
            else:
                column, condition = i.split(":")
                column = column.strip()  # Ensure no leading/trailing whitespaces
                condition = condition.strip()
                # Build the rule string
                #rulestring = f" (df[{json.dumps(column)}] {condition}) "
                if "contains" in condition:
                    substring = condition.split("'")[1]  # Assuming the substring is quoted
                    print(f"Debug: Searching for substring: {substring}")  # Debug print
                    rulestring = f"(df[{json.dumps(column)}].str.contains('{substring}', na=False))"
                else:
                    rulestring = f"(df[{json.dumps(column)}] {condition})"
                flt += rulestring
        df_filtered = df[eval(flt)]
        if df_filtered.empty:
            print("No rows match the filter criteria.")
        else:
            #print("Filtered DataFrame:")
            #print(df_filtered)
            return df_filtered



def top_n_by_column(df, sortcols_json, printcol, topn):
    if sortcols_json:
        apply_sorting(df, sortcols_json)
        #print(df)
        sort_params = json.loads(sortcols_json)
        sort_cols = list(sort_params.keys())
        if not printcol:
            printcol = sort_cols[0]  # Default to the first sorting column
        columns_to_return = list(dict.fromkeys(sort_cols + [printcol]))
        return df[columns_to_return].head(topn)


def process_multifile(mfileopt):
    files, ops = mfileopt.split(":")
    f1, f2 = files.split(",")
    df1 = read_csv(f1)
    df2 = read_csv(f2)
    df = pd.DataFrame()
    for op in ops.split(","):
        col, crule = op.split(";")
        df[col.strip()] = pd.eval(crule.strip(), locals={"df1": df1, "df2": df2})
    return df

def main():
    args = parse_arguments()

    if args.multifile:
        df = process_multifile(args.multifile)
    elif args.inputfile:
        #df = read_csv(args.inputfile)
        df, dforig = read_and_clean_csv(args.inputfile)
    else:
        print("No input file provided for single or multiple file processing. Exiting.")
        sys.exit(1)

    # Apply rules first if --applyrulefirst is set
    if args.applyrulefirst and args.rule:
        df = apply_rules(df, args.rule)

    if args.addcol:
        add_new_columns(df, args.addcol)

    if args.aggregatecolumns:
        colname, colpat, metric = args.aggregatecolumns.split(":")
        pat = re.compile(colpat)
        cols = df.columns
        newcols = list(filter(pat.match, cols))
        if metric == "mean":
            df[colname] = df[newcols].mean(axis=1)
        elif metric == "max":
            df[colname] = df[newcols].max(axis=1)
        elif metric == "min":
            df[colname] = df[newcols].min(axis=1)
        else:
            print("Metric not defined\n")
            exit(1)
    else:
        pass

    if  args.printcol and args.topn:
        df_top_n = top_n_by_column(df, args.sortcol, args.printcol, args.topn)
        #print(df_top_n.columns)
        if df_top_n is not None:
            df = df_top_n

    # Apply rules at the end if --applyrulefirst is not set and rules are specified
    if not args.applyrulefirst and args.rule:
        df = apply_rules(df, args.rule)

    if args.extraprintcols:
        extra_cols = args.extraprintcols.split(',')
        for col in extra_cols:
            if col in dforig.columns:
                print(f"All columns in orig {dforig.columns} \n")
                df[col] = dforig[col]
            else:
                print(f"column: {col} no defined\n")

    if args.outputfile:
        df.to_csv(args.outputfile, sep=",", index=False)
    else:
        #print('*' * 30)
        #print(df.to_string(index=False))
        import json

# Assuming 'df' is your DataFrame
        result = df.to_dict(orient='records')  # Convert DataFrame to a list of dicts
        print(json.dumps(result, indent=2))  # Print JSON string of the result


if __name__ == "__main__":
    main()

