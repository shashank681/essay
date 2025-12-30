# product_manager.py - Complete Updated Script
import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import json
import time
from datetime import datetime, timedelta
import os
from pathlib import Path
from io import BytesIO  # Added for Excel/CSV buffers

# Page config
st.set_page_config(
    page_title="Hulara - WooCommerce Product Manager",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
    }
    .product-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: #f9f9f9;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .user-message {
        background: #e3f2fd;
        text-align: right;
    }
    .ai-message {
        background: #f5f5f5;
        text-align: left;
    }
    .visibility-badge {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .visible { background: #c8e6c9; color: #2e7d32; }
    .catalog { background: #fff9c4; color: #f57f17; }
    .search { background: #b3e5fc; color: #0277bd; }
    .hidden { background: #ffcdd2; color: #c62828; }
</style>
""", unsafe_allow_html=True)

# ============ Credential Storage Functions ============
def get_config_path():
    """Get path to config file"""
    return Path.home() / ".hulara_config.json"

def load_saved_credentials():
    """Load saved credentials from local file"""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def save_credentials(store_url, consumer_key, consumer_secret, ai_provider, ai_api_key):
    """Save credentials to local file"""
    config_path = get_config_path()
    config = {
        "store_url": store_url,
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "ai_provider": ai_provider,
        "ai_api_key": ai_api_key
    }
    with open(config_path, 'w') as f:
        json.dump(config, f)

def delete_saved_credentials():
    """Delete saved credentials"""
    config_path = get_config_path()
    if config_path.exists():
        os.remove(config_path)

# ============ API Helper Functions ============
@st.cache_data(ttl=300)
def get_products_cached(store_url, consumer_key, consumer_secret, page=1, per_page=20):
    """Cached API call to get products"""
    try:
        response = requests.get(
            f"{store_url}/wp-json/wc/v3/products",
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            params={"page": page, "per_page": per_page},
            timeout=30
        )
        if response.status_code == 200:
            return response.json(), response.headers.get('X-WP-Total', 0)
        return [], 0
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return [], 0

def get_all_products(store_url, consumer_key, consumer_secret):
    """Get all products with pagination"""
    all_products = []
    page = 1
    per_page = 100
   
    while True:
        try:
            response = requests.get(
                f"{store_url}/wp-json/wc/v3/products",
                auth=HTTPBasicAuth(consumer_key, consumer_secret),
                params={"page": page, "per_page": per_page},
                timeout=30
            )
            if response.status_code == 200:
                products = response.json()
                if not products:
                    break
                all_products.extend(products)
                page += 1
                time.sleep(0.5) # Rate limiting
            else:
                break
        except:
            break
   
    return all_products

def get_product_by_id(store_url, consumer_key, consumer_secret, product_id):
    """Get single product by ID"""
    try:
        response = requests.get(
            f"{store_url}/wp-json/wc/v3/products/{product_id}",
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def update_product(store_url, consumer_key, consumer_secret, product_id, data):
    """Update product"""
    try:
        response = requests.put(
            f"{store_url}/wp-json/wc/v3/products/{product_id}",
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            json=data,
            timeout=30
        )
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def delete_product(store_url, consumer_key, consumer_secret, product_id, force=False):
    """Delete product"""
    try:
        response = requests.delete(
            f"{store_url}/wp-json/wc/v3/products/{product_id}",
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            params={"force": force},
            timeout=30
        )
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def create_product(store_url, consumer_key, consumer_secret, data):
    """Create new product"""
    try:
        response = requests.post(
            f"{store_url}/wp-json/wc/v3/products",
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            json=data,
            timeout=30
        )
        return response.status_code == 201, response.json() if response.status_code == 201 else response.text
    except Exception as e:
        return False, str(e)

def get_orders(store_url, consumer_key, consumer_secret, days=30):
    """Get orders from last N days"""
    try:
        after_date = (datetime.now() - timedelta(days=days)).isoformat()
        response = requests.get(
            f"{store_url}/wp-json/wc/v3/orders",
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            params={"after": after_date, "per_page": 100},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_product_variations(store_url, consumer_key, consumer_secret, product_id):
    """Get variations for a variable product"""
    try:
        response = requests.get(
            f"{store_url}/wp-json/wc/v3/products/{product_id}/variations",
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            params={"per_page": 100},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def create_variation(store_url, consumer_key, consumer_secret, product_id, data):
    """Create product variation"""
    try:
        response = requests.post(
            f"{store_url}/wp-json/wc/v3/products/{product_id}/variations",
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            json=data,
            timeout=30
        )
        return response.status_code == 201, response.json() if response.status_code == 201 else response.text
    except Exception as e:
        return False, str(e)

def get_product_reviews(store_url, consumer_key, consumer_secret, product_id=None):
    """Get product reviews"""
    try:
        params = {"per_page": 100}
        if product_id:
            params["product"] = product_id
        response = requests.get(
            f"{store_url}/wp-json/wc/v3/products/reviews",
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            params=params,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def update_review(store_url, consumer_key, consumer_secret, review_id, data):
    """Update review"""
    try:
        response = requests.put(
            f"{store_url}/wp-json/wc/v3/products/reviews/{review_id}",
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            json=data,
            timeout=30
        )
        return response.status_code == 200
    except:
        return False

def delete_review(store_url, consumer_key, consumer_secret, review_id, force=True):
    """Delete review"""
    try:
        response = requests.delete(
            f"{store_url}/wp-json/wc/v3/products/reviews/{review_id}",
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            params={"force": force},
            timeout=30
        )
        return response.status_code == 200
    except:
        return False

# ============ AI Chatbot Functions ============
def call_openai_api(api_key, messages):
    """Call OpenAI ChatGPT API"""
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 1000
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def call_gemini_api(api_key, messages):
    """Call Google Gemini API - FIXED MODEL NAME"""
    try:
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
       
        # Use correct model name: gemini-1.5-flash or gemini-pro
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={"contents": contents},
            timeout=60
        )
       
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # Try with gemini-pro as fallback
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}",
                headers={"Content-Type": "application/json"},
                json={"contents": contents},
                timeout=60
            )
            if response.status_code == 200:
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_ai_response(provider, api_key, user_message, context=""):
    """Get AI response based on provider"""
    system_message = f"""You are a helpful WooCommerce product management assistant.
    Help users with:
    - Writing product titles, descriptions, and keywords
    - SEO optimization suggestions
    - Product categorization advice
    - Pricing strategies
    - Review responses
   
    Current context: {context}
   
    Be concise and practical in your responses."""
   
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
   
    if provider == "OpenAI (ChatGPT)":
        return call_openai_api(api_key, messages)
    else:
        return call_gemini_api(api_key, messages)

# ============ UI Components ============
def show_visibility_badge(visibility):
    """Show visibility badge"""
    badges = {
        "visible": '<span class="visibility-badge visible">✅ Visible</span>',
        "catalog": '<span class="visibility-badge catalog">📁 Catalog Only</span>',
        "search": '<span class="visibility-badge search">🔍 Search Only</span>',
        "hidden": '<span class="visibility-badge hidden">🚫 Hidden</span>'
    }
    return badges.get(visibility, visibility)

def login_page():
    """Login page with credential saving option"""
    st.title("🛍️ Hulara - WooCommerce Product Manager")
    st.markdown("---")
   
    # Load saved credentials
    saved_creds = load_saved_credentials()
   
    col1, col2, col3 = st.columns([1, 2, 1])
   
    with col2:
        st.subheader("🔐 Connect Your Store")
       
        # Pre-fill with saved credentials
        default_url = saved_creds.get("store_url", "") if saved_creds else ""
        default_key = saved_creds.get("consumer_key", "") if saved_creds else ""
        default_secret = saved_creds.get("consumer_secret", "") if saved_creds else ""
        default_ai_provider = saved_creds.get("ai_provider", "OpenAI (ChatGPT)") if saved_creds else "OpenAI (ChatGPT)"
        default_ai_key = saved_creds.get("ai_api_key", "") if saved_creds else ""
       
        store_url = st.text_input("Store URL", value=default_url, placeholder="https://yourstore.com")
        consumer_key = st.text_input("Consumer Key", value=default_key, placeholder="ck_xxxxxxxx")
        consumer_secret = st.text_input("Consumer Secret", value=default_secret, type="password", placeholder="cs_xxxxxxxx")
       
        st.markdown("---")
        st.subheader("🤖 AI Assistant (Optional)")
       
        ai_providers = ["OpenAI (ChatGPT)", "Google (Gemini)"]
        ai_provider_index = ai_providers.index(default_ai_provider) if default_ai_provider in ai_providers else 0
        ai_provider = st.selectbox("AI Provider", ai_providers, index=ai_provider_index)
        ai_api_key = st.text_input("AI API Key", value=default_ai_key, type="password", placeholder="Your API key")
       
        st.markdown("---")
       
        # Save credentials option
        save_creds = st.checkbox("💾 Save credentials locally", value=bool(saved_creds))
       
        col_btn1, col_btn2 = st.columns(2)
       
        with col_btn1:
            if st.button("🚀 Connect", type="primary", use_container_width=True):
                if store_url and consumer_key and consumer_secret:
                    # Test connection
                    with st.spinner("Connecting..."):
                        try:
                            response = requests.get(
                                f"{store_url}/wp-json/wc/v3/products",
                                auth=HTTPBasicAuth(consumer_key, consumer_secret),
                                params={"per_page": 1},
                                timeout=30
                            )
                            if response.status_code == 200:
                                st.session_state.logged_in = True
                                st.session_state.store_url = store_url.rstrip('/')
                                st.session_state.consumer_key = consumer_key
                                st.session_state.consumer_secret = consumer_secret
                                st.session_state.ai_provider = ai_provider
                                st.session_state.ai_api_key = ai_api_key
                               
                                # Save credentials if requested
                                if save_creds:
                                    save_credentials(store_url, consumer_key, consumer_secret, ai_provider, ai_api_key)
                               
                                st.success("✅ Connected successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ Connection failed: {response.status_code}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("Please fill all required fields")
       
        with col_btn2:
            if saved_creds and st.button("🗑️ Delete Saved", use_container_width=True):
                delete_saved_credentials()
                st.success("Saved credentials deleted!")
                time.sleep(1)
                st.rerun()

def ai_chatbot_sidebar():
    """AI Chatbot in sidebar"""
    if not st.session_state.get('ai_api_key'):
        st.sidebar.info("💡 Add AI API key on login to enable chatbot")
        return
   
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 AI Assistant")
   
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
   
    # Chat container
    chat_container = st.sidebar.container()
   
    # Display chat history
    with chat_container:
        for msg in st.session_state.chat_history[-5:]: # Show last 5 messages
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 {msg["content"]}</div>',
                           unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message ai-message">🤖 {msg["content"]}</div>',
                           unsafe_allow_html=True)
   
    # Input
    user_input = st.sidebar.text_input("Ask AI...", key="ai_input", placeholder="Help me write a product title...")
   
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("📤 Send", use_container_width=True):
            if user_input:
                # Add user message
                st.session_state.chat_history.append({"role": "user", "content": user_input})
               
                # Get context
                context = ""
                if 'current_product' in st.session_state and st.session_state.current_product:
                    p = st.session_state.current_product
                    context = f"Current product: {p.get('name', 'N/A')}, Price: {p.get('price', 'N/A')}"
               
                # Get AI response
                with st.spinner("Thinking..."):
                    response = get_ai_response(
                        st.session_state.ai_provider,
                        st.session_state.ai_api_key,
                        user_input,
                        context
                    )
               
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
   
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

def listing_update_tab():
    """Listing update tab with variations and delete"""
    st.header("📝 Listing Update")
   
    # Get products
    products, total = get_products_cached(
        st.session_state.store_url,
        st.session_state.consumer_key,
        st.session_state.consumer_secret,
        page=1, per_page=100
    )
   
    if not products:
        st.warning("No products found")
        return
   
    # Product selector
    product_options = {f"{p['id']} - {p['name']}": p['id'] for p in products}
    selected = st.selectbox("Select Product", list(product_options.keys()))
   
    if selected:
        product_id = product_options[selected]
        product = get_product_by_id(
            st.session_state.store_url,
            st.session_state.consumer_key,
            st.session_state.consumer_secret,
            product_id
        )
       
        if product:
            st.session_state.current_product = product
           
            # Show visibility badge
            st.markdown(show_visibility_badge(product.get('catalog_visibility', 'visible')),
                       unsafe_allow_html=True)
           
            # Tabs for different actions
            tab1, tab2, tab3, tab4 = st.tabs(["📝 Edit Details", "🎨 Variations", "➕ Add Variation", "🗑️ Delete"])
           
            with tab1:
                # Basic details form
                with st.form("update_form"):
                    name = st.text_input("Product Name", value=product.get('name', ''))
                   
                    col1, col2 = st.columns(2)
                    with col1:
                        regular_price = st.text_input("Regular Price", value=product.get('regular_price', ''))
                    with col2:
                        sale_price = st.text_input("Sale Price", value=product.get('sale_price', ''))
                   
                    description = st.text_area("Description", value=product.get('description', ''), height=150)
                    short_description = st.text_area("Short Description", value=product.get('short_description', ''), height=100)
                   
                    # Visibility
                    visibility_options = ["visible", "catalog", "search", "hidden"]
                    current_visibility = product.get('catalog_visibility', 'visible')
                    visibility_index = visibility_options.index(current_visibility) if current_visibility in visibility_options else 0
                    visibility = st.selectbox("Visibility", visibility_options, index=visibility_index)
                   
                    # Tags
                    current_tags = ", ".join([t['name'] for t in product.get('tags', [])])
                    tags_input = st.text_input("Tags (comma separated)", value=current_tags)
                   
                    # SKU and Stock
                    col1, col2 = st.columns(2)
                    with col1:
                        sku = st.text_input("SKU", value=product.get('sku', ''))
                    with col2:
                        stock = st.number_input("Stock Quantity", value=product.get('stock_quantity') or 0)
                   
                    submitted = st.form_submit_button("💾 Update Product", type="primary")
                   
                    if submitted:
                        # Prepare tags
                        tags = [{"name": t.strip()} for t in tags_input.split(",") if t.strip()]
                       
                        update_data = {
                            "name": name,
                            "regular_price": regular_price,
                            "sale_price": sale_price,
                            "description": description,
                            "short_description": short_description,
                            "catalog_visibility": visibility,
                            "tags": tags,
                            "sku": sku,
                            "stock_quantity": int(stock) if stock else None,
                            "manage_stock": True if stock else False
                        }
                       
                        success, result = update_product(
                            st.session_state.store_url,
                            st.session_state.consumer_key,
                            st.session_state.consumer_secret,
                            product_id,
                            update_data
                        )
                       
                        if success:
                            st.success("✅ Product updated!")
                            get_products_cached.clear()
                        else:
                            st.error(f"❌ Error: {result}")
           
            with tab2:
                # Show existing variations
                if product.get('type') == 'variable':
                    variations = get_product_variations(
                        st.session_state.store_url,
                        st.session_state.consumer_key,
                        st.session_state.consumer_secret,
                        product_id
                    )
                   
                    if variations:
                        st.subheader(f"📦 {len(variations)} Variations")
                        for var in variations:
                            attrs = var.get('attributes', [])
                            attr_str = ", ".join([f"{a['name']}: {a['option']}" for a in attrs])
                           
                            with st.expander(f"🏷️ {var.get('sku', 'No SKU')} - {attr_str}"):
                                st.write(f"**Price:** ₹{var.get('regular_price', 'N/A')}")
                                st.write(f"**Sale Price:** ₹{var.get('sale_price', 'N/A')}")
                                st.write(f"**Stock:** {var.get('stock_quantity', 'N/A')}")
                                if var.get('image'):
                                    st.image(var['image'].get('src', ''), width=100)
                    else:
                        st.info("No variations found")
                else:
                    st.info("This is a simple product. Convert to variable product to add variations.")
           
            with tab3:
                # Add new variation
                st.subheader("➕ Add New Variation")
               
                # Get product attributes
                attributes = product.get('attributes', [])
               
                if not attributes:
                    st.warning("No attributes defined. Add attributes first.")
                else:
                    with st.form("add_variation_form"):
                        st.write("**Select Attributes:**")
                       
                        variation_attrs = []
                        for attr in attributes:
                            if attr.get('variation', False):
                                selected_option = st.selectbox(
                                    attr['name'],
                                    attr.get('options', []),
                                    key=f"attr_{attr['name']}"
                                )
                                variation_attrs.append({
                                    "name": attr['name'],
                                    "option": selected_option
                                })
                       
                        col1, col2 = st.columns(2)
                        with col1:
                            var_sku = st.text_input("Variation SKU")
                            var_price = st.text_input("Regular Price")
                        with col2:
                            var_sale_price = st.text_input("Sale Price")
                            var_stock = st.number_input("Stock", min_value=0, value=0)
                       
                        var_image = st.text_input("Image URL (optional)")
                       
                        if st.form_submit_button("➕ Add Variation", type="primary"):
                            # First ensure product is variable type
                            if product.get('type') != 'variable':
                                update_product(
                                    st.session_state.store_url,
                                    st.session_state.consumer_key,
                                    st.session_state.consumer_secret,
                                    product_id,
                                    {"type": "variable"}
                                )
                           
                            # Create variation
                            var_data = {
                                "regular_price": var_price,
                                "sale_price": var_sale_price,
                                "sku": var_sku,
                                "stock_quantity": int(var_stock),
                                "manage_stock": True,
                                "attributes": variation_attrs
                            }
                           
                            if var_image:
                                var_data["image"] = {"src": var_image}
                           
                            success, result = create_variation(
                                st.session_state.store_url,
                                st.session_state.consumer_key,
                                st.session_state.consumer_secret,
                                product_id,
                                var_data
                            )
                           
                            if success:
                                st.success("✅ Variation added!")
                                get_products_cached.clear()
                            else:
                                st.error(f"❌ Error: {result}")
           
            with tab4:
                # Delete product
                st.subheader("🗑️ Delete Product")
                st.warning(f"⚠️ You are about to delete: **{product.get('name')}**")
               
                col1, col2 = st.columns(2)
                with col1:
                    trash_btn = st.button("🗑️ Move to Trash", type="secondary", use_container_width=True)
                with col2:
                    permanent_btn = st.button("❌ Delete Permanently", type="primary", use_container_width=True)
               
                if trash_btn:
                    success, result = delete_product(
                        st.session_state.store_url,
                        st.session_state.consumer_key,
                        st.session_state.consumer_secret,
                        product_id,
                        force=False
                    )
                    if success:
                        st.success("✅ Product moved to trash!")
                        get_products_cached.clear()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result}")
               
                if permanent_btn:
                    confirm = st.checkbox("I understand this cannot be undone")
                    if confirm:
                        success, result = delete_product(
                            st.session_state.store_url,
                            st.session_state.consumer_key,
                            st.session_state.consumer_secret,
                            product_id,
                            force=True
                        )
                        if success:
                            st.success("✅ Product permanently deleted!")
                            get_products_cached.clear()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result}")

def product_list_tab():
    """Product list with visibility and quick actions"""
    st.header("📦 Product List")
   
    # Pagination
    col1, col2 = st.columns([3, 1])
    with col2:
        page = st.number_input("Page", min_value=1, value=1)
   
    products, total = get_products_cached(
        st.session_state.store_url,
        st.session_state.consumer_key,
        st.session_state.consumer_secret,
        page=page, per_page=20
    )
   
    st.write(f"**Total Products:** {total}")
   
    if products:
        for product in products:
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
               
                with col1:
                    images = product.get('images', [])
                    if images:
                        st.image(images[0].get('src', ''), width=80)
                    else:
                        st.write("🖼️")
               
                with col2:
                    st.write(f"**{product.get('name', 'N/A')}**")
                    st.caption(f"SKU: {product.get('sku', 'N/A')} | Type: {product.get('type', 'simple')}")
                    st.markdown(show_visibility_badge(product.get('catalog_visibility', 'visible')),
                               unsafe_allow_html=True)
               
                with col3:
                    st.write(f"₹{product.get('price', 'N/A')}")
                    st.caption(f"Stock: {product.get('stock_quantity', '∞')}")
               
                with col4:
                    if st.button("✏️", key=f"edit_{product['id']}"):
                        st.session_state.edit_product_id = product['id']
                        st.info(f"Go to Listing Update tab to edit product ID: {product['id']}")
               
                st.markdown("---")

def safe_excel_export(df, filename, mime_type):
    """Safely export DataFrame to Excel with fallback to CSV"""
    try:
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')  # Explicit engine
        buffer.seek(0)
        st.download_button(
            f"📥 Download {filename}",
            data=buffer,
            file_name=filename,
            mime=mime_type
        )
        return True
    except Exception as e:
        st.error(f"Excel export failed: {str(e)}. Falling back to CSV...")
        buffer = BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        csv_filename = filename.replace('.xlsx', '.csv')
        st.download_button(
            f"📥 Download CSV Fallback ({csv_filename})",
            data=buffer,
            file_name=csv_filename,
            mime="text/csv"
        )
        return False

def bulk_upload_tab():
    """Bulk upload via Excel"""
    st.header("📤 Bulk Upload")
   
    # Download template
    st.subheader("1️⃣ Download Template")
   
    template_data = {
        "name": ["Sample Product 1", "Sample Product 2"],
        "sku": ["SKU001", "SKU002"],
        "regular_price": ["999", "1499"],
        "sale_price": ["899", "1299"],
        "description": ["Product description here", "Another description"],
        "short_description": ["Short desc", "Short desc 2"],
        "categories": ["Category1", "Category2"],
        "tags": ["tag1, tag2", "tag3"],
        "images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
        "stock_quantity": [100, 50],
        "catalog_visibility": ["visible", "visible"]
    }
   
    template_df = pd.DataFrame(template_data)
   
    # Safe export
    safe_excel_export(template_df, "product_upload_template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
   
    st.markdown("---")
    st.subheader("2️⃣ Upload Products")
   
    uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'])
   
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("**Preview:**")
        st.dataframe(df.head())
       
        if st.button("🚀 Upload Products", type="primary"):
            progress = st.progress(0)
            status = st.empty()
           
            success_count = 0
            error_count = 0
           
            for idx, row in df.iterrows():
                progress.progress((idx + 1) / len(df))
                status.text(f"Uploading {idx + 1}/{len(df)}: {row.get('name', 'Unknown')}")
               
                # Prepare product data
                product_data = {
                    "name": str(row.get('name', '')),
                    "sku": str(row.get('sku', '')),
                    "regular_price": str(row.get('regular_price', '')),
                    "sale_price": str(row.get('sale_price', '')),
                    "description": str(row.get('description', '')),
                    "short_description": str(row.get('short_description', '')),
                    "catalog_visibility": str(row.get('catalog_visibility', 'visible'))
                }
               
                # Categories
                if pd.notna(row.get('categories')):
                    product_data["categories"] = [{"name": c.strip()} for c in str(row['categories']).split(",")]
               
                # Tags
                if pd.notna(row.get('tags')):
                    product_data["tags"] = [{"name": t.strip()} for t in str(row['tags']).split(",")]
               
                # Images
                if pd.notna(row.get('images')):
                    product_data["images"] = [{"src": img.strip()} for img in str(row['images']).split(",")]
               
                # Stock
                if pd.notna(row.get('stock_quantity')):
                    product_data["stock_quantity"] = int(row['stock_quantity'])
                    product_data["manage_stock"] = True
               
                success, result = create_product(
                    st.session_state.store_url,
                    st.session_state.consumer_key,
                    st.session_state.consumer_secret,
                    product_data
                )
               
                if success:
                    success_count += 1
                else:
                    error_count += 1
               
                time.sleep(0.5) # Rate limiting
           
            progress.progress(1.0)
            status.text("Complete!")
           
            st.success(f"✅ Uploaded: {success_count} | ❌ Errors: {error_count}")
            get_products_cached.clear()

def analytics_tab():
    """Analytics with visibility stats"""
    st.header("📊 Analytics & Visibility Stats")
   
    # Time period selector
    period = st.selectbox("Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days"])
    days = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}[period]
   
    # Get data
    with st.spinner("Loading analytics..."):
        products = get_all_products(
            st.session_state.store_url,
            st.session_state.consumer_key,
            st.session_state.consumer_secret
        )
        orders = get_orders(
            st.session_state.store_url,
            st.session_state.consumer_key,
            st.session_state.consumer_secret,
            days=days
        )
   
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
   
    with col1:
        st.metric("📦 Total Products", len(products))
   
    with col2:
        st.metric("🛒 Orders", len(orders))
   
    with col3:
        total_revenue = sum(float(o.get('total', 0)) for o in orders)
        st.metric("💰 Revenue", f"₹{total_revenue:,.0f}")
   
    with col4:
        avg_order = total_revenue / len(orders) if orders else 0
        st.metric("📈 Avg Order", f"₹{avg_order:,.0f}")
   
    st.markdown("---")
   
    # Visibility Distribution
    st.subheader("👁️ Product Visibility Distribution")
   
    visibility_counts = {"visible": 0, "catalog": 0, "search": 0, "hidden": 0}
    for p in products:
        vis = p.get('catalog_visibility', 'visible')
        visibility_counts[vis] = visibility_counts.get(vis, 0) + 1
   
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Visible", visibility_counts['visible'])
    with col2:
        st.metric("📁 Catalog Only", visibility_counts['catalog'])
    with col3:
        st.metric("🔍 Search Only", visibility_counts['search'])
    with col4:
        st.metric("🚫 Hidden", visibility_counts['hidden'])
   
    # Visibility chart
    vis_df = pd.DataFrame({
        "Visibility": list(visibility_counts.keys()),
        "Count": list(visibility_counts.values())
    })
    st.bar_chart(vis_df.set_index("Visibility"))
   
    st.markdown("---")
   
    # Product Status Overview
    st.subheader("📊 Product Status Overview")
   
    col1, col2 = st.columns(2)
   
    with col1:
        # Stock status
        in_stock = sum(1 for p in products if p.get('stock_status') == 'instock')
        out_of_stock = sum(1 for p in products if p.get('stock_status') == 'outofstock')
       
        st.write("**Stock Status:**")
        st.write(f"✅ In Stock: {in_stock}")
        st.write(f"❌ Out of Stock: {out_of_stock}")
   
    with col2:
        # Product types
        types = {}
        for p in products:
            t = p.get('type', 'simple')
            types[t] = types.get(t, 0) + 1
       
        st.write("**Product Types:**")
        for t, count in types.items():
            st.write(f"• {t.title()}: {count}")
   
    st.markdown("---")
   
    # Top Selling Products
    st.subheader("🏆 Top Selling Products")
   
    product_sales = {}
    for order in orders:
        for item in order.get('line_items', []):
            pid = item.get('product_id')
            product_sales[pid] = product_sales.get(pid, 0) + item.get('quantity', 0)
   
    if product_sales:
        sorted_sales = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:10]
       
        for pid, qty in sorted_sales:
            product = next((p for p in products if p['id'] == pid), None)
            if product:
                st.write(f"• **{product.get('name', 'Unknown')}** - {qty} sold")
    else:
        st.info("No sales data available for this period")
   
    st.markdown("---")
   
    # Listing Quality Issues
    st.subheader("⚠️ Listing Quality Issues")
   
    issues = {
        "Missing Images": [],
        "No Description": [],
        "No Price": [],
        "Hidden Products": [],
        "No Tags": []
    }
   
    for p in products:
        if not p.get('images'):
            issues["Missing Images"].append(p['name'])
        if not p.get('description'):
            issues["No Description"].append(p['name'])
        if not p.get('regular_price'):
            issues["No Price"].append(p['name'])
        if p.get('catalog_visibility') == 'hidden':
            issues["Hidden Products"].append(p['name'])
        if not p.get('tags'):
            issues["No Tags"].append(p['name'])
   
    for issue, products_list in issues.items():
        if products_list:
            with st.expander(f"❌ {issue} ({len(products_list)})"):
                for name in products_list[:20]: # Show first 20
                    st.write(f"• {name}")
                if len(products_list) > 20:
                    st.write(f"... and {len(products_list) - 20} more")

def reviews_tab():
    """Reviews management tab"""
    st.header("⭐ Reviews Management")
   
    # Get reviews
    with st.spinner("Loading reviews..."):
        reviews = get_product_reviews(
            st.session_state.store_url,
            st.session_state.consumer_key,
            st.session_state.consumer_secret
        )
   
    if not reviews:
        st.info("No reviews found")
        return
   
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Total Reviews", len(reviews))
    with col2:
        avg_rating = sum(r.get('rating', 0) for r in reviews) / len(reviews) if reviews else 0
        st.metric("⭐ Average Rating", f"{avg_rating:.1f}")
    with col3:
        pending = sum(1 for r in reviews if r.get('status') == 'hold')
        st.metric("⏳ Pending Approval", pending)
   
    st.markdown("---")
   
    # Filter
    filter_status = st.selectbox("Filter by Status", ["All", "Approved", "Pending", "Spam"])
   
    filtered_reviews = reviews
    if filter_status == "Approved":
        filtered_reviews = [r for r in reviews if r.get('status') == 'approved']
    elif filter_status == "Pending":
        filtered_reviews = [r for r in reviews if r.get('status') == 'hold']
    elif filter_status == "Spam":
        filtered_reviews = [r for r in reviews if r.get('status') == 'spam']
   
    # Display reviews
    for review in filtered_reviews:
        with st.expander(f"{'⭐' * review.get('rating', 0)} - {review.get('reviewer', 'Anonymous')}"):
            st.write(f"**Product ID:** {review.get('product_id')}")
            st.write(f"**Date:** {review.get('date_created', 'N/A')[:10]}")
            st.write(f"**Status:** {review.get('status', 'N/A')}")
            st.write(f"**Review:** {review.get('review', 'No content')}")
           
            col1, col2, col3 = st.columns(3)
           
            with col1:
                if st.button("✅ Approve", key=f"approve_{review['id']}"):
                    if update_review(
                        st.session_state.store_url,
                        st.session_state.consumer_key,
                        st.session_state.consumer_secret,
                        review['id'],
                        {"status": "approved"}
                    ):
                        st.success("Approved!")
                        st.rerun()
           
            with col2:
                if st.button("🚫 Spam", key=f"spam_{review['id']}"):
                    if update_review(
                        st.session_state.store_url,
                        st.session_state.consumer_key,
                        st.session_state.consumer_secret,
                        review['id'],
                        {"status": "spam"}
                    ):
                        st.success("Marked as spam!")
                        st.rerun()
           
            with col3:
                if st.button("🗑️ Delete", key=f"delete_review_{review['id']}"):
                    if delete_review(
                        st.session_state.store_url,
                        st.session_state.consumer_key,
                        st.session_state.consumer_secret,
                        review['id']
                    ):
                        st.success("Deleted!")
                        st.rerun()

def reports_tab():
    """Reports download tab"""
    st.header("📥 Reports")
   
    col1, col2 = st.columns(2)
   
    with col1:
        st.subheader("📦 All Products Report")
        if st.button("📥 Generate Products Report", use_container_width=True):
            with st.spinner("Generating report..."):
                products = get_all_products(
                    st.session_state.store_url,
                    st.session_state.consumer_key,
                    st.session_state.consumer_secret
                )
               
                # Prepare data including variations
                report_data = []
                progress = st.progress(0)
               
                for idx, p in enumerate(products):
                    progress.progress((idx + 1) / len(products))
                   
                    # Parent product
                    report_data.append({
                        "ID": p['id'],
                        "Parent ID": "",
                        "Type": p.get('type', 'simple'),
                        "SKU": p.get('sku', ''),
                        "Name": p.get('name', ''),
                        "Regular Price": p.get('regular_price', ''),
                        "Sale Price": p.get('sale_price', ''),
                        "Stock": p.get('stock_quantity', ''),
                        "Visibility": p.get('catalog_visibility', ''),
                        "Categories": ", ".join([c['name'] for c in p.get('categories', [])]),
                        "Tags": ", ".join([t['name'] for t in p.get('tags', [])])
                    })
                   
                    # Get variations if variable
                    if p.get('type') == 'variable':
                        variations = get_product_variations(
                            st.session_state.store_url,
                            st.session_state.consumer_key,
                            st.session_state.consumer_secret,
                            p['id']
                        )
                        for var in variations:
                            attrs = var.get('attributes', [])
                            attr_str = ", ".join([f"{a['name']}: {a['option']}" for a in attrs])
                            report_data.append({
                                "ID": var['id'],
                                "Parent ID": p['id'],
                                "Type": "variation",
                                "SKU": var.get('sku', ''),
                                "Name": f"{p.get('name', '')} - {attr_str}",
                                "Regular Price": var.get('regular_price', ''),
                                "Sale Price": var.get('sale_price', ''),
                                "Stock": var.get('stock_quantity', ''),
                                "Visibility": "",
                                "Categories": "",
                                "Tags": ""
                            })
                        time.sleep(0.3)
               
                df = pd.DataFrame(report_data)
               
                # Safe export
                safe_excel_export(
                    df,
                    f"products_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
   
    with col2:
        st.subheader("🛒 Orders Report")
        days = st.number_input("Days", min_value=7, max_value=365, value=30)
       
        if st.button("📥 Generate Orders Report", use_container_width=True):
            with st.spinner("Generating report..."):
                orders = get_orders(
                    st.session_state.store_url,
                    st.session_state.consumer_key,
                    st.session_state.consumer_secret,
                    days=days
                )
               
                report_data = []
                for o in orders:
                    report_data.append({
                        "Order ID": o['id'],
                        "Date": o.get('date_created', '')[:10],
                        "Status": o.get('status', ''),
                        "Total": o.get('total', ''),
                        "Customer": f"{o.get('billing', {}).get('first_name', '')} {o.get('billing', {}).get('last_name', '')}",
                        "Email": o.get('billing', {}).get('email', ''),
                        "Items": len(o.get('line_items', []))
                    })
               
                df = pd.DataFrame(report_data)
               
                # Safe export
                safe_excel_export(
                    df,
                    f"orders_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

def main():
    """Main application"""
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
   
    if not st.session_state.logged_in:
        login_page()
    else:
        # Sidebar
        st.sidebar.title("🛍️ Hulara")
        st.sidebar.write(f"Connected: {st.session_state.store_url}")
       
        if st.sidebar.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
       
        # AI Chatbot in sidebar
        ai_chatbot_sidebar()
       
        # Main tabs
        tabs = st.tabs([
            "📝 Listing Update",
            "📦 Product List",
            "📤 Bulk Upload",
            "📊 Analytics",
            "⭐ Reviews",
            "📥 Reports"
        ])
       
        with tabs[0]:
            listing_update_tab()
       
        with tabs[1]:
            product_list_tab()
       
        with tabs[2]:
            bulk_upload_tab()
       
        with tabs[3]:
            analytics_tab()
       
        with tabs[4]:
            reviews_tab()
       
        with tabs[5]:
            reports_tab()

if __name__ == "__main__":
    main()
