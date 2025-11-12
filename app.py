import streamlit as st
import json
from datetime import datetime
from api_manager import APIManager
from database import Database
from comparator import ResponseComparator

# Initialize
db = Database()
api_manager = APIManager()
comparator = ResponseComparator()

st.set_page_config(page_title="API Comparator", layout="wide")
st.title("🔄 API Testing & Comparison Tool")

# Sidebar for navigation
menu = st.sidebar.selectbox(
    "Menu",
    ["API Configuration", "Execute Tests", "Compare Results", "View History"]
)

# ==================== API Configuration ====================
if menu == "API Configuration":
    st.header("⚙️ API Configuration")
    
    st.info("💡 **Tip:** Create TWO configurations with the SAME task name - one for 'Before Change' and one for 'After Change'")
    
    tab1, tab2 = st.tabs(["➕ Add New Configuration", "📋 View All Configurations"])
    
    with tab1:
        st.subheader("Add API Configuration")
        
        # Task name input
        task_name = st.text_input(
            "Task Name *", 
            placeholder="e.g., GetFlight_Comparison",
            help="Use the same task name for both 'Before' and 'After' versions"
        )
        
        # Show visual guide
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🔴 Before Change API")
            api_version = st.radio(
                "Select API Version:",
                ["Before Change", "After Change"],
                index=0,
                help="Choose which version you're configuring now"
            )
        
        with col2:
            st.markdown("### 🟢 After Change API")
            st.caption("Configure this after saving the 'Before Change' version")
        
        st.divider()
        
        # API Details
        col1, col2 = st.columns(2)
        
        with col1:
            api_url = st.text_input(
                "API Endpoint *", 
                placeholder="https://api.example.com/getflight",
                help="Full URL of the API endpoint"
            )
            method = st.selectbox("HTTP Method *", ["POST", "GET", "PUT", "DELETE"])
        
        with col2:
            auth_type = st.selectbox(
                "Authentication Type", 
                ["Bearer Token", "API Key", "Basic Auth", "None"]
            )
            
            if auth_type == "Bearer Token":
                token = st.text_input("Bearer Token *", type="password")
            elif auth_type == "API Key":
                api_key = st.text_input("API Key *", type="password")
                key_name = st.text_input("Key Name", value="X-API-Key")
            elif auth_type == "Basic Auth":
                username = st.text_input("Username *")
                password = st.text_input("Password *", type="password")
        
        st.divider()
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("💾 Save Configuration", type="primary", use_container_width=True):
                if not task_name:
                    st.error("❌ Please enter a task name")
                elif not api_url:
                    st.error("❌ Please enter an API endpoint")
                else:
                    auth_details = {}
                    if auth_type == "Bearer Token":
                        auth_details = {"type": "bearer", "token": token}
                    elif auth_type == "API Key":
                        auth_details = {"type": "api_key", "key": api_key, "key_name": key_name}
                    elif auth_type == "Basic Auth":
                        auth_details = {"type": "basic", "username": username, "password": password}
                    
                    config_id = db.save_api_config(
                        task_name=task_name,
                        api_version=api_version,
                        api_url=api_url,
                        method=method,
                        auth_details=json.dumps(auth_details)
                    )
                    st.success(f"✅ Configuration saved! Now add the other version if you haven't already.")
                    st.balloons()
    
    with tab2:
        st.subheader("All Saved Configurations")
        
        configs = db.get_all_configs()
        if configs:
            # Group by task name
            tasks_dict = {}
            for config in configs:
                task = config['task_name']
                if task not in tasks_dict:
                    tasks_dict[task] = []
                tasks_dict[task].append(config)
            
            # Display grouped by task
            for task_name, task_configs in tasks_dict.items():
                st.markdown(f"### 📦 {task_name}")
                
                col1, col2 = st.columns(2)
                
                # Before Change
                before_config = next((c for c in task_configs if c['api_version'] == 'Before Change'), None)
                with col1:
                    if before_config:
                        st.markdown("#### 🔴 Before Change")
                        st.write(f"**URL:** `{before_config['api_url']}`")
                        st.write(f"**Method:** {before_config['method']}")
                        st.write(f"**Created:** {before_config['created_at']}")
                        if st.button(f"🗑️ Delete", key=f"del_before_{before_config['id']}"):
                            db.delete_config(before_config['id'])
                            st.rerun()
                    else:
                        st.warning("⚠️ No 'Before Change' version configured")
                
                # After Change
                after_config = next((c for c in task_configs if c['api_version'] == 'After Change'), None)
                with col2:
                    if after_config:
                        st.markdown("#### 🟢 After Change")
                        st.write(f"**URL:** `{after_config['api_url']}`")
                        st.write(f"**Method:** {after_config['method']}")
                        st.write(f"**Created:** {after_config['created_at']}")
                        if st.button(f"🗑️ Delete", key=f"del_after_{after_config['id']}"):
                            db.delete_config(after_config['id'])
                            st.rerun()
                    else:
                        st.warning("⚠️ No 'After Change' version configured")
                
                st.divider()
        else:
            st.info("📝 No configurations saved yet. Add your first configuration in the 'Add New Configuration' tab!")

# ==================== Execute Tests ====================
elif menu == "Execute Tests":
    st.header("🚀 Execute API Tests")
    
    # Select task and version
    tasks = db.get_all_tasks()
    if not tasks:
        st.warning("⚠️ No API configurations found. Please add one first.")
    else:
        selected_task = st.selectbox("Select Task", tasks)
        configs_for_task = db.get_configs_by_task(selected_task)
        
        config_options = {f"{c['api_version']} - {c['api_url']}": c for c in configs_for_task}
        selected_config_name = st.selectbox("Select API Configuration", list(config_options.keys()))
        selected_config = config_options[selected_config_name]
        
        st.divider()
        
        # Test Case Name
        test_case_name = st.text_input("Test Case Name", placeholder="e.g., TestCase_1_ValidFlightNumber")
        
        # Request Payload
        st.subheader("Request Payload")
        payload_input_method = st.radio("Input Method", ["JSON Editor", "Form Input"])
        
        if payload_input_method == "JSON Editor":
            payload_text = st.text_area(
                "Request Body (JSON)",
                height=200,
                placeholder='{\n  "flightNumber": "AA123",\n  "date": "2025-11-12"\n}'
            )
            try:
                payload = json.loads(payload_text) if payload_text else {}
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format")
                payload = {}
        else:
            st.info("Build your payload using key-value pairs")
            num_fields = st.number_input("Number of fields", min_value=1, max_value=20, value=2)
            payload = {}
            for i in range(num_fields):
                col1, col2 = st.columns(2)
                with col1:
                    key = st.text_input(f"Key {i+1}", key=f"key_{i}")
                with col2:
                    value = st.text_input(f"Value {i+1}", key=f"val_{i}")
                if key:
                    payload[key] = value
        
        # Query Parameters (for GET requests)
        if selected_config['method'] == 'GET':
            st.subheader("Query Parameters")
            query_params = st.text_input("Query Params (key1=value1&key2=value2)")
        else:
            query_params = ""
        
        # Execute Button
        col1, col2 = st.columns([1, 4])
        with col1:
            execute_btn = st.button("▶️ Execute Test", type="primary")
        
        if execute_btn:
            if not test_case_name:
                st.error("❌ Please provide a test case name")
            else:
                with st.spinner("Executing API call..."):
                    try:
                        response = api_manager.execute_request(
                            config=selected_config,
                            payload=payload,
                            query_params=query_params
                        )
                        
                        # Save to database
                        db.save_test_result(
                            config_id=selected_config['id'],
                            test_case_name=test_case_name,
                            request_payload=json.dumps(payload),
                            response_data=json.dumps(response['body']),
                            status_code=response['status_code'],
                            response_time=response['response_time']
                        )
                        
                        st.success(f"✅ Test executed successfully!")
                        
                        # Display Results
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Status Code", response['status_code'])
                        col2.metric("Response Time", f"{response['response_time']:.2f}s")
                        col3.metric("Response Size", f"{len(str(response['body']))} bytes")
                        
                        st.subheader("Response")
                        st.json(response['body'])
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# ==================== Compare Results ====================
elif menu == "Compare Results":
    st.header("🔍 Compare API Responses")
    
    tasks = db.get_all_tasks()
    if not tasks:
        st.warning("⚠️ No test results found.")
    else:
        selected_task = st.selectbox("Select Task to Compare", tasks)
        
        # Get test cases for this task
        test_cases = db.get_test_cases_by_task(selected_task)
        
        if not test_cases:
            st.info("No test cases found for this task.")
        else:
            selected_test_case = st.selectbox("Select Test Case", test_cases)
            
            # Get results for both versions
            results = db.get_results_for_comparison(selected_task, selected_test_case)
            
            if len(results) < 2:
                st.warning("⚠️ Need results from both 'Before Change' and 'After Change' versions to compare.")
                st.info(f"Found {len(results)} version(s). Please run tests for both versions.")
            else:
                before = next((r for r in results if r['api_version'] == 'Before Change'), None)
                after = next((r for r in results if r['api_version'] == 'After Change'), None)
                
                if before and after:
                    st.divider()
                    
                    # Metrics comparison
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Status Code Change",
                            after['status_code'],
                            delta=after['status_code'] - before['status_code']
                        )
                    with col2:
                        time_diff = after['response_time'] - before['response_time']
                        st.metric(
                            "Response Time (After)",
                            f"{after['response_time']:.2f}s",
                            delta=f"{time_diff:+.2f}s"
                        )
                    with col3:
                        responses_match = before['response_data'] == after['response_data']
                        st.metric(
                            "Responses Match",
                            "✅ Yes" if responses_match else "❌ No"
                        )
                    
                    st.divider()
                    
                    # Side-by-side comparison
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🔴 Before Change")
                        st.write(f"**Executed:** {before['executed_at']}")
                        st.json(json.loads(before['response_data']))
                    
                    with col2:
                        st.subheader("🟢 After Change")
                        st.write(f"**Executed:** {after['executed_at']}")
                        st.json(json.loads(after['response_data']))
                    
                    # Detailed Diff
                    st.divider()
                    st.subheader("📊 Detailed Difference Analysis")
                    
                    diff_result = comparator.compare_responses(
                        json.loads(before['response_data']),
                        json.loads(after['response_data'])
                    )
                    
                    if diff_result['identical']:
                        st.success("✅ Responses are identical!")
                    else:
                        st.warning("⚠️ Differences detected:")
                        for diff in diff_result['differences']:
                            st.write(f"- {diff}")
                        
                        # Show detailed diff
                        with st.expander("View Detailed JSON Diff"):
                            st.json(diff_result)

# ==================== View History ====================
elif menu == "View History":
    st.header("📜 Test Execution History")
    
    tasks = db.get_all_tasks()
    if tasks:
        filter_task = st.selectbox("Filter by Task", ["All"] + tasks)
        
        if filter_task == "All":
            history = db.get_all_test_results()
        else:
            history = db.get_test_results_by_task(filter_task)
        
        if history:
            for result in history:
                with st.expander(
                    f"{'✅' if result['status_code'] == 200 else '❌'} "
                    f"{result['task_name']} - {result['test_case_name']} "
                    f"({result['api_version']})"
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Executed:** {result['executed_at']}")
                        st.write(f"**Status Code:** {result['status_code']}")
                        st.write(f"**Response Time:** {result['response_time']:.2f}s")
                    with col2:
                        st.write(f"**API URL:** {result['api_url']}")
                        st.write(f"**Method:** {result['method']}")
                    
                    st.write("**Request:**")
                    st.json(json.loads(result['request_payload']))
                    
                    st.write("**Response:**")
                    st.json(json.loads(result['response_data']))
        else:
            st.info("No test results found.")
    else:
        st.info("No test history available.")
