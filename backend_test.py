#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class RRideGarageAPITester:
    def __init__(self, base_url="https://partsride.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.test_user_mobile = f"9876543{datetime.now().strftime('%H%M')}"
        self.test_password = "TestPass123!"

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
            self.failed_tests.append({"test": name, "error": details})

    def make_request(self, method, endpoint, data=None, auth_required=False):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return None, f"Unsupported method: {method}"
            
            return response, None
        except requests.exceptions.RequestException as e:
            return None, str(e)

    def test_database_seeding(self):
        """Test if database is seeded with products"""
        response, error = self.make_request('POST', 'seed')
        if error:
            self.log_test("Database Seeding", False, error)
            return False
        
        success = response.status_code in [200, 400]  # 400 if already seeded
        if success and response.status_code == 200:
            data = response.json()
            success = "products_count" in data
        
        self.log_test("Database Seeding", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_user_registration(self):
        """Test user registration"""
        user_data = {
            "mobile": self.test_user_mobile,
            "password": self.test_password,
            "name": "Test User"
        }
        
        response, error = self.make_request('POST', 'auth/register', user_data)
        if error:
            self.log_test("User Registration", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = "token" in data and "user" in data
            if success:
                self.token = data["token"]
                self.user_id = data["user"]["id"]
        
        self.log_test("User Registration", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_user_login(self):
        """Test user login"""
        login_data = {
            "mobile": self.test_user_mobile,
            "password": self.test_password
        }
        
        response, error = self.make_request('POST', 'auth/login', login_data)
        if error:
            self.log_test("User Login", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = "token" in data and "user" in data
            if success:
                self.token = data["token"]
                self.user_id = data["user"]["id"]
        
        self.log_test("User Login", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_get_user_profile(self):
        """Test getting user profile"""
        response, error = self.make_request('GET', 'auth/me', auth_required=True)
        if error:
            self.log_test("Get User Profile", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = "id" in data and "mobile" in data
        
        self.log_test("Get User Profile", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_get_products(self):
        """Test getting all products"""
        response, error = self.make_request('GET', 'products')
        if error:
            self.log_test("Get Products", False, error)
            return False, []
        
        success = response.status_code == 200
        products = []
        if success:
            products = response.json()
            success = isinstance(products, list) and len(products) > 0
        
        self.log_test("Get Products", success, 
                     f"Status: {response.status_code}, Count: {len(products)}" if success else f"Status: {response.status_code}")
        return success, products

    def test_get_product_detail(self, product_id):
        """Test getting product detail"""
        response, error = self.make_request('GET', f'products/{product_id}')
        if error:
            self.log_test("Get Product Detail", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = "id" in data and "name" in data and "price" in data
        
        self.log_test("Get Product Detail", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_get_categories(self):
        """Test getting categories"""
        response, error = self.make_request('GET', 'categories')
        if error:
            self.log_test("Get Categories", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = isinstance(data, list) and len(data) == 4
            expected_categories = ["Performance", "Safety Gear", "Pro Spares", "Accessories"]
            if success:
                category_names = [cat["name"] for cat in data]
                success = all(cat in category_names for cat in expected_categories)
        
        self.log_test("Get Categories", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_get_bike_brands(self):
        """Test getting bike brands"""
        response, error = self.make_request('GET', 'bikes/brands')
        if error:
            self.log_test("Get Bike Brands", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = isinstance(data, list) and len(data) == 4
            expected_brands = ["KTM", "BMW", "Royal Enfield", "Yamaha"]
            if success:
                brand_names = [brand["name"] for brand in data]
                success = all(brand in brand_names for brand in expected_brands)
        
        self.log_test("Get Bike Brands", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_get_bike_models(self):
        """Test getting bike models for KTM"""
        response, error = self.make_request('GET', 'bikes/models/KTM')
        if error:
            self.log_test("Get Bike Models", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = isinstance(data, list) and len(data) > 0
            expected_models = ["Duke 390", "Duke 250", "RC 390", "Adventure 390"]
            if success:
                success = all(model in data for model in expected_models)
        
        self.log_test("Get Bike Models", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_get_bike_variants(self):
        """Test getting bike variants"""
        response, error = self.make_request('GET', 'bikes/variants/KTM/Duke%20390')
        if error:
            self.log_test("Get Bike Variants", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = isinstance(data, list) and len(data) > 0
        
        self.log_test("Get Bike Variants", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_add_to_cart(self, product_id):
        """Test adding product to cart"""
        cart_data = {
            "product_id": product_id,
            "quantity": 2
        }
        
        response, error = self.make_request('POST', 'cart/add', cart_data, auth_required=True)
        if error:
            self.log_test("Add to Cart", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = "message" in data
        
        self.log_test("Add to Cart", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_get_cart(self):
        """Test getting cart contents"""
        response, error = self.make_request('GET', 'cart', auth_required=True)
        if error:
            self.log_test("Get Cart", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = "items" in data and len(data["items"]) > 0
        
        self.log_test("Get Cart", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_update_cart(self, product_id):
        """Test updating cart item quantity"""
        update_data = {
            "product_id": product_id,
            "quantity": 3
        }
        
        response, error = self.make_request('POST', 'cart/update', update_data, auth_required=True)
        if error:
            self.log_test("Update Cart", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = "message" in data
        
        self.log_test("Update Cart", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_create_order(self, product_id):
        """Test creating an order"""
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "product_name": "Test Product",
                    "quantity": 1,
                    "price": 1000
                }
            ],
            "total_amount": 1000,
            "shipping_address": {
                "name": "Test User",
                "mobile": self.test_user_mobile,
                "address_line": "123 Test Street",
                "city": "Test City",
                "state": "Test State",
                "pincode": "123456"
            },
            "payment_method": "cod"
        }
        
        response, error = self.make_request('POST', 'orders/create', order_data, auth_required=True)
        if error:
            self.log_test("Create Order", False, error)
            return False, None
        
        success = response.status_code == 200
        order_id = None
        if success:
            data = response.json()
            success = "id" in data
            if success:
                order_id = data["id"]
        
        self.log_test("Create Order", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success, order_id

    def test_get_orders(self):
        """Test getting user orders"""
        response, error = self.make_request('GET', 'orders', auth_required=True)
        if error:
            self.log_test("Get Orders", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = isinstance(data, list)
        
        self.log_test("Get Orders", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_get_order_detail(self, order_id):
        """Test getting order detail"""
        if not order_id:
            self.log_test("Get Order Detail", False, "No order ID provided")
            return False
        
        response, error = self.make_request('GET', f'orders/{order_id}', auth_required=True)
        if error:
            self.log_test("Get Order Detail", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = "id" in data and "items" in data
        
        self.log_test("Get Order Detail", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def test_payment_create_order(self):
        """Test Razorpay order creation"""
        response, error = self.make_request('POST', 'payment/create-order', {"amount": 1000}, auth_required=True)
        if error:
            self.log_test("Payment Create Order", False, error)
            return False
        
        success = response.status_code == 200
        if success:
            data = response.json()
            success = "key_id" in data and "amount" in data and "currency" in data
        
        self.log_test("Payment Create Order", success, 
                     f"Status: {response.status_code}" if not success else "")
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting RRIDE GARAGE API Tests...")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test database seeding
        self.test_database_seeding()
        
        # Test user registration and authentication
        if not self.test_user_registration():
            print("❌ Registration failed, trying login with existing user...")
            if not self.test_user_login():
                print("❌ Both registration and login failed. Stopping tests.")
                return self.generate_report()
        
        # Test authenticated endpoints
        self.test_get_user_profile()
        
        # Test product endpoints
        products_success, products = self.test_get_products()
        if products_success and products:
            # Test product detail with first product
            self.test_get_product_detail(products[0]["id"])
            
            # Test cart operations with first product
            product_id = products[0]["id"]
            if self.test_add_to_cart(product_id):
                self.test_get_cart()
                self.test_update_cart(product_id)
                
                # Test order operations
                order_success, order_id = self.test_create_order(product_id)
                if order_success:
                    self.test_get_orders()
                    self.test_get_order_detail(order_id)
        
        # Test category and bike endpoints
        self.test_get_categories()
        self.test_get_bike_brands()
        self.test_get_bike_models()
        self.test_get_bike_variants()
        
        # Test payment endpoints
        self.test_payment_create_order()
        
        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_run}")
        print(f"❌ Tests Failed: {len(self.failed_tests)}/{self.tests_run}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  • {test['test']}: {test['error']}")
        
        print("\n" + "=" * 60)
        
        # Return success if more than 80% tests pass
        return self.tests_passed / self.tests_run >= 0.8

def main():
    """Main function"""
    tester = RRideGarageAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 Backend API tests completed successfully!")
        return 0
    else:
        print("💥 Backend API tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())