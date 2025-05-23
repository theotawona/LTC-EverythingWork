import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


##### Functions 

#### Interest Functions

# Function to parse dates
def parse_date(date_str):
    if pd.isna(date_str):
        return None
    try:
        # Try different formats
        formats = ['%d/%m/%Y', '%Y-%m-%d']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    except:
        return None



# Function to calculate compound interest for periods with exact 12-month cycles
def calculate_interest(row):
    occupation_date = row['Occupation Date']
    vacating_date = row['Vacating Date']
    current_deposit = row['Current Deposit']
    
    if pd.isna(occupation_date) or pd.isna(vacating_date) or pd.isna(current_deposit):
        return None
    
    # Define the rate change date
    rate_change_date = datetime(2023, 1, 1)
    
    # Initialize variables
    periods = []
    running_deposit = current_deposit
    total_interest = 0
    current_date = occupation_date
    
    # Generate yearly periods
    while current_date < vacating_date:
        # Calculate the end of this yearly period
        # If we're at the exact same day, add one year
        next_year_date = current_date + relativedelta(years=1)
        
        # If the next year date is beyond vacating date, use vacating date
        period_end = min(next_year_date, vacating_date)
        
        # Calculate how much of a full year this period represents
        if next_year_date <= vacating_date:
            # This is a full year
            fraction_of_year = 1.0
        else:
            # This is a partial year - calculate months and days precisely
            months_diff = relativedelta(period_end, current_date).months
            years_diff = relativedelta(period_end, current_date).years
            days_diff = relativedelta(period_end, current_date).days
            
            # Calculate fraction based on months (each month = 1/12 of year)
            fraction_of_year = years_diff + (months_diff / 12) + (days_diff / 365)
        
        # Determine the interest rate for this period
        if current_date < rate_change_date:
            rate = 0.02  # 2% before 2023
        else:
            rate = 0.03  # 3% from 2023 onwards
        
        # Calculate interest for this period - use exact percentage for full years
        if fraction_of_year == 1.0:
            interest = running_deposit * rate
        else:
            interest = running_deposit * rate * fraction_of_year
        
        # Round the interest to 2 decimal places
        interest = round(interest, 2)
        
        # Update running deposit with the earned interest (compound interest)
        new_deposit = running_deposit + interest
        
        # Store this period's information
        periods.append({
            'period_start': current_date.strftime('%d/%m/%Y'),
            'period_end': period_end.strftime('%d/%m/%Y'),
            'deposit_at_start': round(running_deposit, 2),
            'rate': rate * 100,
            'interest': interest,
            'deposit_after_interest': round(new_deposit, 2)
        })
        
        # Update for the next period
        total_interest += interest
        running_deposit = new_deposit
        current_date = next_year_date
        
        # Break if we've reached or gone past the vacating date
        if current_date >= vacating_date:
            break
    
    return {
        'periods': periods,
        'total_interest': round(total_interest, 2),
        'final_deposit': round(running_deposit, 2)
    }


# Function to generate a styled HTML table for each tenant
def generate_tenant_table(row):
    tenant_name = row['Tenant Name']
    tenant_code = row['Tenant Code']
    property_name = row['Property']
    unit_number = row['Unit Number']
    initial_deposit = row['Initial Deposit']
    current_deposit = row['Current Deposit']
    occupation_date = row['Occupation Date']
    vacating_date = row['Vacating Date']
    periods = row['Periods']
    total_interest = row['Total Interest']
    final_amount = row['Final Amount']
    
    # Create HTML for the header
    html = f"""
    <div style="margin-bottom: 20px; border: 1px solid #ddd; padding: 15px; border-radius: 5px;">
        <h3 style="color: #2c3e50; margin-top: 0;">{tenant_name} (Code: {tenant_code})</h3>
        <div style="display: flex; flex-wrap: wrap;">
            <div style="margin-right: 20px;">
                <strong>Property:</strong> {property_name}<br>
                <strong>Unit:</strong> {unit_number}<br>
            </div>
            <div style="margin-right: 20px;">
                <strong>Initial Deposit:</strong> R{initial_deposit:.2f}<br>
                <strong>Current Deposit:</strong> R{current_deposit:.2f}<br>
            </div>
            <div>
                <strong>Occupation Date:</strong> {occupation_date}<br>
                <strong>Vacating Date:</strong> {vacating_date}<br>
            </div>
        </div>
        
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Period</th>
                    <th style="padding: 8px; text-align: right; border: 1px solid #ddd;">Deposit at Start</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid #ddd;">Rate</th>
                    <th style="padding: 8px; text-align: right; border: 1px solid #ddd;">Interest Earned</th>
                    <th style="padding: 8px; text-align: right; border: 1px solid #ddd;">Deposit After Interest</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Add rows for each period
    for period in periods:
        html += f"""
                <tr>
                    <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">{period['period_start']} to {period['period_end']}</td>
                    <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">R{period['deposit_at_start']:.2f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{period['rate']:.1f}%</td>
                    <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">R{period['interest']:.2f}</td>
                    <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">R{period['deposit_after_interest']:.2f}</td>
                </tr>
        """
    
    # Add summary row
    html += f"""
            </tbody>
            <tfoot>
                <tr style="background-color: #f9f9f9; font-weight: bold;">
                    <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">TOTAL</td>
                    <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">R{current_deposit:.2f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">-</td>
                    <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">R{total_interest:.2f}</td>
                    <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">R{final_amount:.2f}</td>
                </tr>
            </tfoot>
        </table>
    </div>
    """
    
    return html

# Create a summary table
def create_summary_table(df):
    summary_html = """
    <div style="margin-bottom: 30px; margin-top: 30px;">
        <h2 style="color: #2c3e50;">Interest Summary for All Tenants</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background-color: #2c3e50; color: white;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Property</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Tenant Name</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Tenant Code</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Unit</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">Current Deposit</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">Total Interest</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">Final Amount</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for idx, row in df.iterrows():
        summary_html += f"""
                <tr>
                    <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">{row['Property']}</td>
                    <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">{row['Tenant Name']}</td>
                    <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">{row['Tenant Code']}</td>
                    <td style="padding: 8px; text-align: left; border: 1px solid #ddd;">{row['Unit Number']}</td>
                    <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">R{row['Current Deposit']:.2f}</td>
                    <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">R{row['Total Interest']:.2f}</td>
                    <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">R{row['Final Amount']:.2f}</td>
                </tr>
        """
    
    # Add totals row
    total_current_deposit = df['Current Deposit'].sum()
    total_interest = df['Total Interest'].sum()
    total_final_amount = df['Final Amount'].sum()
    
    summary_html += f"""
            </tbody>
            <tfoot>
                <tr style="background-color: #f2f2f2; font-weight: bold;">
                    <td style="padding: 10px; text-align: left; border: 1px solid #ddd;" colspan="4">TOTAL</td>
                    <td style="padding: 10px; text-align: right; border: 1px solid #ddd;">R{total_current_deposit:.2f}</td>
                    <td style="padding: 10px; text-align: right; border: 1px solid #ddd;">R{total_interest:.2f}</td>
                    <td style="padding: 10px; text-align: right; border: 1px solid #ddd;">R{total_final_amount:.2f}</td>
                </tr>
            </tfoot>
        </table>
    </div>
    """
    
    return summary_html

# Generate all tenant tables and summary table
def generate_full_report(df):
    full_html = f"""
    <div style="font-family: Arial, sans-serif;">
        <h1 style="color: #2c3e50; text-align: center;">Tenant Deposit Interest Calculation</h1>
        <p style="text-align: center; margin-bottom: 30px;">Calculated as of {datetime.now().strftime('%d %B %Y')}</p>
        
        {create_summary_table(df)}
        
        <h2 style="color: #2c3e50; margin-top: 40px;">Detailed Calculations by Tenant</h2>
    """
    
    for idx, row in df.iterrows():
        full_html += generate_tenant_table(row)
    
    full_html += """
    </div>
    """
    
    return full_html


#### Early Payers Function

     



######

st.title("Everything Work")
st.write("#### This is a tool for automating generation of Early Payers List and Calculation of Interest Earned on Deposit Held")
st.divider()

tab1, tab2 = st.tabs(["Process Early Payers", "Process Interest"])
months =["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

with tab1:
    st.subheader("Process Your Early Payers Here")
    property = st.selectbox(label="Property", options=["Rand Daily Mail", "Solly Sachs House", "Shell House"])
    col1, col2, col3 = st.columns(3)
    month = col1.selectbox(label="Month", options=months)
    date = col2.date_input(label="Exclude Leases Starting After")
    receipt_date = col3.date_input(label="Receipts On and Before:")

    
    tenant_trans = st.file_uploader(label="Drop a Tenant Transactions CSV Here", type=["csv"])

    calc_early_payers = st.button("Generate Early Payers", use_container_width=True, type="primary")

    if calc_early_payers:
        tt = pd.read_csv(tenant_trans)
        # Convert date columns to datetime
        date_columns = ['VacateDate','LeaseStartDate']
        for col in date_columns:
            tt[col] = tt[col].apply(parse_date)
        pd.set_option('display.float_format', lambda x: '%.f' %x)
        tt = tt[['TenantCode', 'ListOrTradingAsName', 'TransactionCode', 'TransactionRemarks', 'EffectiveDate', 'BalanceDate', 'BalanceBf', 'InclusiveAmount','VacateDate', 'LeaseStartDate', 'MainUnitNo']]
        tt_copy = tt.copy()
        tt_copy["TransactionCode"].fillna("b/f", inplace=True)
        tt_copy["EffectiveDate"].fillna(tt_copy["BalanceDate"], inplace=True)
        tt_copy["InclusiveAmount"].fillna(tt_copy["BalanceBf"], inplace=True)
        tt_copy["LeaseStartDate"] = pd.to_datetime(tt_copy["LeaseStartDate"], format="%d/%m/%Y").dt.date
        tt_copy["EffectiveDate"] = pd.to_datetime(tt_copy["EffectiveDate"], format="%d/%m/%Y").dt.date
        tt_copy = tt_copy[tt_copy["LeaseStartDate"]< date]
        tt_copy = tt_copy[tt_copy["VacateDate"].isnull()]
        tt_copy.drop(columns=["VacateDate", 'LeaseStartDate', 'BalanceBf', 'BalanceDate'], inplace=True)
        tt_copy = tt_copy[tt_copy["EffectiveDate"]<  receipt_date]
        tt_copy_pivot = tt_copy.pivot_table(
            index=["TenantCode","ListOrTradingAsName", "MainUnitNo"],
            values=["InclusiveAmount"],
            aggfunc='sum'
                )
        tt_copy_pivot_EP = tt_copy_pivot[tt_copy_pivot["InclusiveAmount"]<=0.00]

        st.write(f"### Early Payers for {month}")
        st.dataframe(tt_copy_pivot_EP, use_container_width=True)
        if property and month:
            st.download_button(
                label=f"Download {month} {property} Early Payers",
                file_name=f"{property}_{month}_early_payers.csv",
                data=tt_copy_pivot_EP.to_csv(),
                mime="text/csv",
                icon=":material/download:",
                )





        


with tab2:
    st.subheader("Process Your Interest Held Here")
    col1, col2 = st.columns(2)
    properties = col1.multiselect(label="Property", options=["Rand Daily Mail", "Solly Sachs House", "Shell House"], key="Prop2")
    month = col2.selectbox(label="Month", options=months, key="month2")
    

    moveouts = st.file_uploader(label="Drop a Moveouts CSV Here", type=["csv"])

    calc_interest = st.button("Calculate Interest", use_container_width=True,type='primary')

    if calc_interest:
        data = pd.read_csv(moveouts)
        # Convert date columns to datetime
        date_columns = ['Notice Date', 'Vacating Date', 'Lease Starts', 'Lease Ends', 'Occupation Date']
        for col in date_columns:
            data[col] = data[col].apply(parse_date)

        # Apply the calculation to each row
        results = []
        for idx, row in data.iterrows():
            tenant_info = row.to_dict()
            interest_info = calculate_interest(row)
    
            if interest_info:
                tenant_result = {
                'Property': tenant_info['Property'],
                'Tenant Name': tenant_info['Tenant Name'],
                'Tenant Code': tenant_info['Tenant Code'],
                'Unit Number': tenant_info['Unit Number'],
                'Initial Deposit': tenant_info['Initial Deposit'],
                'Current Deposit': tenant_info['Current Deposit'],
                'Occupation Date': tenant_info['Occupation Date'].strftime('%d/%m/%Y'),
                'Vacating Date': tenant_info['Vacating Date'].strftime('%d/%m/%Y'),
                'Periods': interest_info['periods'],
                'Total Interest': interest_info['total_interest'],
                'Final Amount': interest_info['final_deposit']
                }
                results.append(tenant_result)

        # Create a DataFrame from the results
        result_df = pd.DataFrame(results)

        # Generate the full report
        full_report = generate_full_report(result_df)

        with st.expander("View Interest Breakdown"):

            st.html(full_report)


        
        
        export_df = pd.DataFrame({
                'Property': result_df['Property'],
                'Tenant Name': result_df['Tenant Name'],
                'Tenant Code': result_df['Tenant Code'],
                'Unit Number': result_df['Unit Number'],
                'Current Deposit': result_df['Current Deposit'],
                'Total Interest': result_df['Total Interest'],
                'Final Amount': result_df['Final Amount']
                     })
        export_df.to_csv('tenant_interest_summary.csv', index=False)

        st.download_button(
            label="Download Interest Summary",
            file_name="interest_summary.csv",
            data=export_df.to_csv(),
            mime="text/csv",
            icon=":material/download:",
                )

        







        

        

    


