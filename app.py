import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='KGS Lead Estimator', layout='wide')
st.title('KGS Lead Estimator')

# Hardcoded options
lead_types = ['end-user', 'distributor', 'installer', 'consultant']
countries = ['BE','NL','UK','IE','FR','IT','ES','PT','DE','DK','SE','FI','NO','PL','TR','ZA','ME']
industries = [
    'hospitality','datacenters','factories','gas & oil','healthcare','education','retail','transportation',
    'manufacturing','energy','government','banking','insurance','telecommunications','construction','real estate',
    'food & beverage','pharmaceutical','mining','utilities','logistics','media','sports','entertainment','other'
]
technologies = ['addressable','conventional','wireless','aspirating smoke detection','linear heat detection','flame detection','evacuation']

# Base values for technology interest
tech_base_values = {
    'addressable': 15000,
    'aspirating smoke detection': 14000,
    'evacuation': 13000,
    'wireless': 9000,
    'conventional': 7000,
    'linear heat detection': 6000,
    'flame detection': 5000
}

lead_type_multiplier = {'end-user':1.2,'distributor':1.5,'installer':1.1,'consultant':1.3}
country_multiplier = {'BE':1.0,'NL':1.0,'UK':1.1,'IE':1.0,'FR':1.0,'IT':1.0,'ES':1.0,'PT':1.0,'DE':1.1,'DK':1.0,'SE':1.0,'FI':1.0,'NO':1.0,'PL':0.9,'TR':0.8,'ZA':0.9,'ME':1.2}
industry_multiplier = {
    'hospitality':1.1,'datacenters':1.4,'factories':1.3,'gas & oil':1.5,'healthcare':1.3,'education':1.2,'retail':1.1,
    'transportation':1.2,'manufacturing':1.3,'energy':1.4,'government':1.2,'banking':1.3,'insurance':1.2,
    'telecommunications':1.3,'construction':1.2,'real estate':1.1,'food & beverage':1.2,'pharmaceutical':1.4,
    'mining':1.5,'utilities':1.3,'logistics':1.2,'media':1.1,'sports':1.1,'entertainment':1.1,'other':1.0
}

# Initialize session state
if 'persons' not in st.session_state:
    st.session_state['persons'] = [{'lead_type':lead_types[0],'country':countries[0],'industry':industries[0],'technology':technologies[0]}]

# Function to render input form for a person
def person_form(index):
    st.subheader(f'Lead {index+1}')
    lead_type = st.selectbox('Lead Type', lead_types, key=f'lead_type_{index}', index=lead_types.index(st.session_state['persons'][index]['lead_type']))
    country = st.selectbox('Country', countries, key=f'country_{index}', index=countries.index(st.session_state['persons'][index]['country']))
    industry = st.selectbox('Industry', industries, key=f'industry_{index}', index=industries.index(st.session_state['persons'][index]['industry']))
    technology = st.selectbox('Technology Interest', technologies, key=f'tech_{index}', index=technologies.index(st.session_state['persons'][index]['technology']))
    return {'lead_type':lead_type,'country':country,'industry':industry,'technology':technology}

# Render forms for existing persons
for i in range(len(st.session_state['persons'])):
    st.session_state['persons'][i] = person_form(i)

# Add new person button
if st.button('Add Next'):
    st.session_state['persons'].append({'lead_type':lead_types[0],'country':countries[0],'industry':industries[0],'technology':technologies[0]})

# Start estimation button
if st.button('Start Estimation'):
    if len(st.session_state['persons']) == 0:
        st.warning('Please add at least one lead.')
    else:
        with st.spinner('Estimating...'):
            estimates = []
            for person in st.session_state['persons']:
                value = tech_base_values.get(person['technology'],5000)
                value *= lead_type_multiplier.get(person['lead_type'],1)
                value *= country_multiplier.get(person['country'],1)
                value *= industry_multiplier.get(person['industry'],1)
                estimates.append(value)

            total_estimate = sum(estimates)
            low = total_estimate * 0.8
            high = total_estimate * 1.2

            st.subheader('Estimation Results')
            col1,col2,col3 = st.columns(3)
            col1.metric('Low Estimate', f"€{low:,.2f}")
            col2.metric('Expected Estimate', f"€{total_estimate:,.2f}")
            col3.metric('High Estimate', f"€{high:,.2f}")

            # Prepare DataFrame for visualization
            df = pd.DataFrame(st.session_state['persons'])
            df['Estimate'] = estimates

            st.markdown('### Visualizations')
            # Group by Technology Interest
            tech_group = df.groupby('technology')['Estimate'].sum().reset_index()
            fig_tech = px.bar(tech_group, x='technology', y='Estimate', title='Lead Value by Technology Interest', color='technology')
            st.plotly_chart(fig_tech, use_container_width=True)

            # Group by Industry
            industry_group = df.groupby('industry')['Estimate'].sum().reset_index()
            fig_industry = px.bar(industry_group, x='industry', y='Estimate', title='Lead Value by Industry', color='industry')
            st.plotly_chart(fig_industry, use_container_width=True)

            # Group by Country
            country_group = df.groupby('country')['Estimate'].sum().reset_index()
            fig_country = px.bar(country_group, x='country', y='Estimate', title='Lead Value by Country', color='country')
            st.plotly_chart(fig_country, use_container_width=True)
