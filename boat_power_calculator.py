import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import graphviz as gv
from io import BytesIO

# Sample user data
users = {
    "johndoe": {"name": "John Doe", "password": "12345", "email": "john@example.com", "phone": "123-456-7890"},
    "janedoe": {"name": "Jane Doe", "password": "67890", "email": "jane@example.com", "phone": "987-654-3210"}
}

# Initialize session state for authentication if not already done
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None

def authenticate(username, password):
    if username in users and users[username]["password"] == password:
        return users[username]
    else:
        return None

# User authentication
if st.session_state.authentication_status is None:
    st.sidebar.header('Login')
    username = st.sidebar.text_input('Username')
    password = st.sidebar.text_input('Password', type='password')
    if st.sidebar.button('Login'):
        user_data = authenticate(username, password)
        if user_data:
            st.session_state.authentication_status = True
            st.session_state.username = username
            st.session_state.user_data = user_data
        else:
            st.sidebar.error('Username or password is incorrect')
else:
    st.sidebar.success(f"Welcome, {st.session_state.user_data['name']}!")
    if st.sidebar.button('Logout'):
        st.session_state.authentication_status = None
        st.session_state.pop('user_data', None)
        st.session_state.pop('username', None)

if st.session_state.authentication_status:
    # Initialize session state for devices if not already done
    if 'devices' not in st.session_state:
        st.session_state.devices = []

    # Initialize session state for start and end locations if not already done
    if 'start_location' not in st.session_state:
        st.session_state.start_location = None
    if 'end_location' not in st.session_state:
        st.session_state.end_location = None

    # Title
    st.title('🚤 Advanced Boat Power Usage Calculator')

    # Tabs for better organization
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "⚙️ Boat Parameters", "🗺️ Route Visualization", "🔌 Devices", 
        "📊 Results", "📁 Historical Data", "🔗 Connection Diagram", "👤 Profile"
    ])

    # Add a style tag for custom CSS to improve mobile responsiveness
    st.markdown("""
        <style>
        /* Custom CSS to improve mobile responsiveness */
        .main .block-container {
            max-width: 100% !important;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .stSlider, .stNumberInput, .stSelectbox {
            width: 100% !important;
        }
        .stDataFrame, .stTable {
            overflow-x: auto;
        }
        </style>
        """, unsafe_allow_html=True)

    with tab1:
        st.header('⚙️ Boat Parameters')
        with st.expander("Set Boat Parameters"):
            col1, col2 = st.columns([1, 1])
            with col1:
                speed = st.slider('Boat Speed (knots)', 0, 50, 10, help="Set the boat speed in knots")
                weight = st.slider('Boat Weight (tons)', 0, 100, 10, help="Set the boat weight in tons")
                duration = st.slider('Duration (hours)', 0, 24, 1, help="Set the duration of the trip in hours")
            with col2:
                boat_type = st.selectbox('Select Boat Type', ['Sailboat', 'Motorboat', 'Yacht'], help="Choose the type of boat")
                engine_type = st.selectbox('Select Engine Type', ['Electric', 'Diesel', 'Gasoline'], help="Choose the type of engine")
                battery_capacity = st.number_input('Battery Capacity (kWh)', min_value=0.0, value=50.0, help="Set the battery capacity in kWh")
                solar_power = st.number_input('Solar Panel Power (kW)', min_value=0.0, value=1.0, help="Set the solar panel power in kW")

        # Battery types and capacities
        with st.expander("Battery Types and Capacities"):
            st.subheader('Battery Types and Capacities')
            battery_types = {
                'Lead-Acid': 50,
                'Lithium-Ion': 100,
                'Nickel-Metal Hydride': 70
            }
            battery_type = st.selectbox('Select Battery Type', list(battery_types.keys()), help="Choose the type of battery")
            selected_battery_capacity = battery_types[battery_type]
            st.write(f'Selected Battery Capacity: {selected_battery_capacity} kWh')

        # Weather conditions
        with st.expander("Weather Conditions"):
            st.subheader('Weather Conditions')
            col1, col2 = st.columns([1, 1])
            with col1:
                wind_speed = st.slider('Wind Speed (knots)', 0, 100, 10, help="Set the wind speed in knots")
            with col2:
                wave_height = st.slider('Wave Height (meters)', 0, 10, 1, help="Set the wave height in meters")

    with tab2:
        st.header('🗺️ Route Visualization')
        st.write("Click on the map to set the start and end points of your route. The first click sets the start point, and the second click sets the end point.")

        m = folium.Map(location=[20, 0], zoom_start=2)

        # Display the map to get the start location
        if st.session_state.start_location:
            folium.Marker(
                [st.session_state.start_location['lat'], st.session_state.start_location['lng']],
                popup="Start Location",
                tooltip="Start Location"
            ).add_to(m)

        # Display the map to get the end location
        if st.session_state.end_location:
            folium.Marker(
                [st.session_state.end_location['lat'], st.session_state.end_location['lng']],
                popup="End Location",
                tooltip="End Location"
            ).add_to(m)

        # Add polyline if both locations are set
        if st.session_state.start_location and st.session_state.end_location:
            folium.PolyLine(
                [(st.session_state.start_location['lat'], st.session_state.start_location['lng']),
                (st.session_state.end_location['lat'], st.session_state.end_location['lng'])],
                color='blue'
            ).add_to(m)
            distance = ((st.session_state.start_location['lat'] - st.session_state.end_location['lat'])**2 + (st.session_state.start_location['lng'] - st.session_state.end_location['lng'])**2)**0.5
            st.write(f'Distance: {distance:.2f} units')

        # Save start and end locations on map click
        output = st_folium(m, width=700, height=500, key="map")
        if output and output['last_clicked']:
            if not st.session_state.start_location:
                st.session_state.start_location = output['last_clicked']
            elif not st.session_state.end_location:
                st.session_state.end_location = output['last_clicked']

    with tab3:
        st.header('🔌 Device Management')
        with st.expander("Add New Device"):
            device_name = st.text_input('Device Name', help="Enter the name of the device")
            device_power = st.number_input('Device Power (W)', min_value=0, value=100, help="Enter the power consumption of the device in watts")
            if st.button('Add Device'):
                st.session_state.devices.append({'name': device_name, 'power': device_power})
                st.experimental_rerun()

        # Display added devices
        if st.session_state.devices:
            st.subheader('Added Devices')
            device_df = pd.DataFrame(st.session_state.devices)
            st.table(device_df)

            # Allow users to remove devices
            with st.expander("Remove Device"):
                device_to_remove = st.selectbox('Select Device to Remove', device_df['name'])
                if st.button('Remove Device'):
                    st.session_state.devices = [d for d in st.session_state.devices if d['name'] != device_to_remove]
                    st.experimental_rerun()

    with tab4:
        st.header('📊 Results')

        # Advanced power calculation
        efficiency_factor = 0.85  # Example efficiency factor
        resistance_factor = 1 + wind_speed * 0.01 + wave_height * 0.1  # Simple resistance factor
        power = speed * weight * 0.1 * resistance_factor / efficiency_factor
        total_power = power * duration

        # Calculate total device power usage
        total_device_power = sum([d['power'] for d in st.session_state.devices]) * duration / 1000  # Convert W to kW

        # Calculate solar power contribution
        solar_contribution = solar_power * duration

        # Calculate net power usage
        net_power_usage = total_power + total_device_power - solar_contribution

        # Calculate battery life
        battery_life_hours = selected_battery_capacity / net_power_usage if net_power_usage > 0 else float('inf')

        # Determine if devices are consuming too much power
        if total_device_power > selected_battery_capacity + solar_contribution:
            st.warning("⚠️ Warning: The devices are consuming more power than the available battery and solar power.")

        # Fuel/Electricity prices
        with st.expander("Fuel/Electricity Prices"):
            st.subheader('Fuel/Electricity Prices')
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                electricity_price = st.number_input('Electricity Price ($ per kWh)', min_value=0.0, value=0.12, help="Set the price of electricity per kWh")
            with col2:
                diesel_price = st.number_input('Diesel Price ($ per liter)', min_value=0.0, value=1.2, help="Set the price of diesel per liter")
            with col3:
                gasoline_price = st.number_input('Gasoline Price ($ per liter)', min_value=0.0, value=1.0, help="Set the price of gasoline per liter")
            fuel_price = {
                'Electric': electricity_price,
                'Diesel': diesel_price,
                'Gasoline': gasoline_price
            }[engine_type]

        # Calculate total cost
        total_cost = net_power_usage * fuel_price

        # Displaying the results
        st.subheader('Summary of Results')
        col1, col2, col3 = st.columns([1, 1, 1])
        col1.metric('Power Required (kW)', f'{power:.2f}')
        col2.metric('Total Power Usage (kWh)', f'{total_power:.2f}')
        col3.metric('Total Cost ($)', f'{total_cost:.2f}')
        col1.metric('Device Power Usage (kWh)', f'{total_device_power:.2f}')
        col2.metric('Solar Power Contribution (kWh)', f'{solar_contribution:.2f}')
        col3.metric('Net Power Usage (kWh)', f'{net_power_usage:.2f}')
        col1.metric('Battery Life (hours)', f'{battery_life_hours:.2f}')

        # Power usage over time
        time = np.arange(0, int(duration) + 1)
        power_usage = net_power_usage / duration * time
        solar_power_generated = solar_power * time  # Solar power generated over time

        # Create a DataFrame for visualization
        df = pd.DataFrame({
            'Time (hours)': time,
            'Net Power Usage (kWh)': power_usage,
            'Solar Power Generated (kWh)': solar_power_generated
        })

        # Plotting power usage and generation over time
        st.subheader('Power Usage and Generation Over Time')
        st.line_chart(df.set_index('Time (hours)'))

        # Additional Visualization - Pie Chart for Power Distribution
        if st.session_state.devices:
            st.subheader('Power Distribution')
            power_distribution = {
                'Boat Power': total_power,
                'Device Power': total_device_power,
                'Solar Contribution': solar_contribution  # Positive for pie chart
            }
            distribution_df = pd.DataFrame(list(power_distribution.items()), columns=['Source', 'Power (kWh)'])
            st.write(distribution_df)
            st.bar_chart(distribution_df.set_index('Source'))

        # Displaying the dataframe
        st.subheader('Detailed Data')
        st.write(df)

        # Option to export results
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv().encode('utf-8')
            st.download_button(
                label="Export Results as CSV",
                data=csv,
                file_name='power_usage_results.csv',
                mime='text/csv',
            )
        with col2:
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            writer.close()
            excel_data = output.getvalue()
            st.download_button(
                label="Export Results as Excel",
                data=excel_data,
                file_name='power_usage_results.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )

    with tab5:
        st.header('📁 Historical Data')
        with st.expander("Upload Historical Power Usage Data"):
            uploaded_file = st.file_uploader("Upload Historical Power Usage Data (CSV)", type="csv")
            
            if uploaded_file:
                historical_data = pd.read_csv(uploaded_file)
                st.subheader('Uploaded Historical Data')
                st.write(historical_data)

                # Assume the historical data contains a 'Time (hours)' column and 'Power Usage (kWh)' column
                if 'Time (hours)' in historical_data.columns and 'Power Usage (kWh)' in historical_data.columns:
                    # Plot historical data and current data for comparison
                    st.subheader('Comparison with Current Calculations')
                    combined_data = pd.merge(df, historical_data, on='Time (hours)', suffixes=('_current', '_historical'))
                    st.line_chart(combined_data.set_index('Time (hours)'))

    with tab6:
        st.header('🔗 Connection Diagram')
        # Create a directed graph
        diagram = gv.Digraph(format='png')
        
        # Add nodes for power sources
        diagram.node('Battery', 'Battery\nCapacity: {:.2f} kWh'.format(selected_battery_capacity))
        diagram.node('Solar', 'Solar Panel\nPower: {:.2f} kW'.format(solar_power))
        
        # Add nodes for devices
        for device in st.session_state.devices:
            diagram.node(device['name'], f"{device['name']}\nPower: {device['power']} W")

        # Add edges to show connections
        diagram.edge('Battery', 'Boat')
        diagram.edge('Solar', 'Boat')
        for device in st.session_state.devices:
            diagram.edge('Boat', device['name'])

        st.graphviz_chart(diagram)

    with tab7:
        st.header('👤 Profile')
        st.subheader('User Profile Information')
        
        with st.form("profile_form"):
            name = st.text_input('Name', value=st.session_state.user_data['name'])
            email = st.text_input('Email', value=st.session_state.user_data['email'])
            phone = st.text_input('Phone', value=st.session_state.user_data['phone'])
            password = st.text_input('Password', type='password', value=st.session_state.user_data['password'])
            if st.form_submit_button('Update Profile'):
                st.session_state.user_data['name'] = name
                st.session_state.user_data['email'] = email
                st.session_state.user_data['phone'] = phone
                st.session_state.user_data['password'] = password
                users[st.session_state.username] = st.session_state.user_data
                st.success('Profile updated successfully')

    # Footer
    st.markdown("""
        ---
        Powered by Streamlit.
    """)
