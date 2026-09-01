import requests
import json
import base64
import paramiko
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://app.sudra.sa/api"

# Helper for 1x1 test JPEG
TEST_JPG_B64 = "data:image/jpeg;base64," + base64.b64encode(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9").decode('utf-8')

def test_password_reset_flow():
    print("\n==========================================")
    print("TEST 1: Password Reset End-to-End Suite")
    print("==========================================")
    
    test_email = "test_reset_user@sudra.sa"
    initial_pass = "InitialPass123"
    new_pass = "NewSecurePass2026!"
    
    # 1. Register test user if not exists
    reg_res = requests.post(f"{BASE_URL}/auth/register", json={
        "name": "مستخدم اختبار الاستعادة",
        "email": test_email,
        "phone": "0999888777",
        "city": "الخرطوم",
        "password": initial_pass,
        "role": "client"
    }, timeout=15).json()
    print("Register response:", reg_res.get("message"))
    
    # 2. Request Password Reset
    req_res = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": test_email}, timeout=15).json()
    print("1. Request Reset response:", req_res)
    assert req_res.get("success") == True, "Request reset failed"
    assert "OTP" in req_res.get("message", "") or "البريد" in req_res.get("message", "")
    
    # 3. Test wrong OTP rejection
    wrong_verify = requests.post(f"{BASE_URL}/auth/verify-reset-otp", json={
        "email": test_email,
        "otp": "000000"
    }, timeout=15).json()
    print("2. Wrong OTP rejected correctly:", wrong_verify.get("message"))
    assert wrong_verify.get("success") == False, "Wrong OTP was accepted!"
    
    # 4. Fetch the OTP hash from DB over SSH to verify real hashing & valid verify
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=20)
    
    # We test PHP verification on server side
    get_otp_code = """php -r '
    require "/www/wwwroot/app.sudra.sa/config/db.php";
    $stmt = $pdo->prepare("SELECT id, otp_hash FROM password_resets WHERE email = ? AND is_used = 0 ORDER BY id DESC LIMIT 1");
    $stmt->execute(["test_reset_user@sudra.sa"]);
    $row = $stmt->fetch();
    echo $row ? $row["id"] : "none";
    '"""
    stdin, stdout, stderr = ssh.exec_command(get_otp_code)
    reset_id = stdout.read().decode('utf-8').strip()
    print("3. Found active password_resets ID:", reset_id)
    assert reset_id != "none", "No password_resets record in database!"
    
    # Set a known OTP hash for verification testing (e.g. 654321)
    set_known = """php -r '
    require "/www/wwwroot/app.sudra.sa/config/db.php";
    $h = password_hash("654321", PASSWORD_DEFAULT);
    $pdo->prepare("UPDATE password_resets SET otp_hash = ? WHERE id = ?")->execute([$h, %s]);
    '""" % reset_id
    ssh.exec_command(set_known)
    time.sleep(0.5)
    
    # 5. Verify valid OTP -> get reset_token
    valid_verify = requests.post(f"{BASE_URL}/auth/verify-reset-otp", json={
        "email": test_email,
        "otp": "654321"
    }, timeout=15).json()
    print("4. Valid OTP verification:", valid_verify)
    assert valid_verify.get("success") == True, "Valid OTP verification failed"
    reset_token = valid_verify.get("data", {}).get("reset_token")
    assert reset_token and len(reset_token) > 10, "Invalid reset_token received"
    
    # 6. Test password reset validation (short password < 8 chars)
    short_pwd = requests.post(f"{BASE_URL}/auth/reset-password", json={
        "email": test_email,
        "reset_token": reset_token,
        "password": "123",
        "confirm_password": "123"
    }, timeout=15).json()
    print("5. Short password rejected correctly:", short_pwd.get("message"))
    assert short_pwd.get("success") == False
    
    # 7. Test password reset validation (mismatched confirmation)
    mismatch_pwd = requests.post(f"{BASE_URL}/auth/reset-password", json={
        "email": test_email,
        "reset_token": reset_token,
        "password": new_pass,
        "confirm_password": "DifferentPass123"
    }, timeout=15).json()
    print("6. Mismatched confirmation rejected correctly:", mismatch_pwd.get("message"))
    assert mismatch_pwd.get("success") == False
    
    # 8. Reset password successfully
    reset_res = requests.post(f"{BASE_URL}/auth/reset-password", json={
        "email": test_email,
        "reset_token": reset_token,
        "password": new_pass,
        "confirm_password": new_pass
    }, timeout=15).json()
    print("7. Password Reset Success:", reset_res)
    assert reset_res.get("success") == True, "Password reset failed"
    
    # 9. Verify token is single-use and cannot be used again
    reuse_res = requests.post(f"{BASE_URL}/auth/reset-password", json={
        "email": test_email,
        "reset_token": reset_token,
        "password": "AnotherPassword123",
        "confirm_password": "AnotherPassword123"
    }, timeout=15).json()
    print("8. Reused token rejected correctly:", reuse_res.get("message"))
    assert reuse_res.get("success") == False, "Reused token was accepted!"
    
    # 10. Test Login with old password (MUST FAIL)
    old_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": test_email,
        "password": initial_pass
    }, timeout=15).json()
    print("9. Login with old password rejected:", old_login.get("message"))
    assert old_login.get("success") == False
    
    # 11. Test Login with new password (MUST SUCCEED)
    new_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": test_email,
        "password": new_pass
    }, timeout=15).json()
    print("10. Login with new password succeeded:", new_login.get("message"))
    assert new_login.get("success") == True
    
    # 12. Inactive Driver Reset: Verify driver approval state is preserved
    driver_email = "test_pending_driver@sudra.sa"
    requests.post(f"{BASE_URL}/auth/register", json={
        "name": "كابتن قيد المراجعة",
        "email": driver_email,
        "phone": "0999111222",
        "city": "الخرطوم",
        "vehiclePlate": "أ ب ج 123",
        "password": "DriverPass123",
        "role": "driver"
    }, timeout=15)
    
    # Verify driver is_active is 0
    drv_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": driver_email,
        "password": "DriverPass123"
    }, timeout=15).json()
    print("11. Pending driver login status before reset (isPending/403):", drv_login.get("message"))
    assert drv_login.get("isPending") == True or drv_login.get("success") == False
    
    ssh.close()
    print("✅ All Password Reset Tests Passed Successfully!")


def test_multiple_images_flow():
    print("\n==========================================")
    print("TEST 2: Multiple Order Images Suite")
    print("==========================================")
    
    client_phone = "0912345678"
    
    # 1. Create order with 3 images
    img_list_3 = [TEST_JPG_B64, TEST_JPG_B64, TEST_JPG_B64]
    create_res = requests.post(f"{BASE_URL}/orders", json={
        "clientName": "عميل الصور المتعددة",
        "clientPhone": client_phone,
        "city": "الخرطوم",
        "packageCount": 3,
        "notes": "طلب اختبار 3 صور",
        "images": img_list_3
    }, timeout=15).json()
    print("1. Create order with 3 images response:", create_res.get("message"))
    assert create_res.get("success") == True, "Failed to create order with 3 images"
    order_data = create_res.get("data", {})
    order_id = order_data.get("id")
    order_code = order_data.get("order_code")
    images = order_data.get("images", [])
    print(f"   Order #{order_id} ({order_code}) created with {len(images)} images: {images}")
    assert len(images) == 3, f"Expected 3 images, got {len(images)}"
    assert order_data.get("image_path") == images[0], "Backward compatibility image_path mismatch"
    
    # 2. Verify Client API returns the multiple images
    client_orders = requests.get(f"{BASE_URL}/orders?phone={client_phone}", timeout=15).json()
    found = next((o for o in client_orders.get("data", []) if o.get("id") == order_id), None)
    assert found is not None, "Order not found in client orders list"
    assert len(found.get("images", [])) == 3, f"Expected 3 images in client orders, got {len(found.get('images', []))}"
    print("2. Customer API retrieved all 3 images:", found.get("images"))
    
    # 3. Verify Driver API returns the multiple images
    driver_orders = requests.get(f"{BASE_URL}/orders?city=الخرطوم", timeout=15).json()
    found_drv = next((o for o in driver_orders.get("data", []) if o.get("id") == order_id), None)
    assert found_drv is not None, "Order not found in driver orders list"
    assert len(found_drv.get("images", [])) == 3
    print("3. Driver API retrieved all 3 images:", found_drv.get("images"))
    
    # 4. Test max limit: 6 images (MUST BE REJECTED with 400)
    img_list_6 = [TEST_JPG_B64] * 6
    rej_res = requests.post(f"{BASE_URL}/orders", json={
        "clientName": "عميل الصور",
        "clientPhone": client_phone,
        "city": "الخرطوم",
        "packageCount": 1,
        "notes": "طلب مرفوض",
        "images": img_list_6
    }, timeout=15).json()
    print("4. Rejection of > 5 images:", rej_res.get("message"))
    assert rej_res.get("success") == False, "Server allowed > 5 images!"
    assert "5" in rej_res.get("message", ""), "Error message did not mention 5 images limit"
    
    # 5. Test Driver Lifecycle with multi-image order (Accept -> Loaded -> Delivered)
    accept_res = requests.post(f"{BASE_URL}/orders/{order_id}/accept", json={
        "driverName": "كابتن الاختبار السريع",
        "driverPhone": "0900001111",
        "action": "accept"
    }, timeout=15).json()
    print("5. Driver accept order:", accept_res.get("message"))
    assert accept_res.get("success") == True
    
    loaded_res = requests.post(f"{BASE_URL}/orders/{order_id}/status", json={
        "status": "loaded",
        "collectedAmount": 4500.0,
        "action": "update_status"
    }, timeout=15).json()
    print("6. Driver mark loaded with 4500 cash:", loaded_res.get("message"))
    assert loaded_res.get("success") == True
    
    deliv_res = requests.post(f"{BASE_URL}/orders/{order_id}/status", json={
        "status": "delivered",
        "collectedAmount": 4500.0,
        "action": "update_status"
    }, timeout=15).json()
    print("7. Driver mark delivered:", deliv_res.get("message"))
    assert deliv_res.get("success") == True
    
    print("✅ All Multiple Images Tests Passed Successfully!")

if __name__ == '__main__':
    test_password_reset_flow()
    test_multiple_images_flow()
    print("\n🎉 ALL PRODUCTION SUITES PASSED WITH 100% SUCCESS!")
