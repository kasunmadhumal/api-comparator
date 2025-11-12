# Quick Reference Guide

## 🚀 Quick Start Commands

### Local Development
```bash
# First time setup
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Run application
streamlit run app.py

# Or use the startup script
./start.sh
```

### AWS EC2 Deployment
```bash
# 1. Upload files to EC2
scp -i your-key.pem -r * ubuntu@YOUR_EC2_IP:~/api-comparator/

# 2. Connect to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# 3. Run deployment script
cd ~/api-comparator
chmod +x deploy-ec2.sh
./deploy-ec2.sh

# 4. Access application
# Open browser: http://YOUR_EC2_IP:8501
```

## 📋 Workflow Example

### Scenario: Testing GetFlight API Changes

#### Step 1: Configure Old API
- Menu: **API Configuration**
- Task Name: `GetFlight_v1_vs_v2`
- API Version: `Before Change`
- URL: `https://api-old.example.com/v1/flights`
- Token: `your-old-api-token`
- Method: `POST`

#### Step 2: Configure New API
- Task Name: `GetFlight_v1_vs_v2` (same as above)
- API Version: `After Change`
- URL: `https://api-new.example.com/v2/flights`
- Token: `your-new-api-token`
- Method: `POST`

#### Step 3: Test Old API
- Menu: **Execute Tests**
- Select: `GetFlight_v1_vs_v2` → `Before Change`
- Test Case Name: `Valid_Flight_AA123`
- Payload:
  ```json
  {
    "flightNumber": "AA123",
    "date": "2025-11-12"
  }
  ```
- Click: **Execute Test**

Repeat with different test cases:
- `Invalid_Flight`
- `International_Flight_BA456`
- `Future_Date`

#### Step 4: Test New API
- Select: `GetFlight_v1_vs_v2` → `After Change`
- Use SAME test case names and payloads
- Execute all tests

#### Step 5: Compare Results
- Menu: **Compare Results**
- Select Task: `GetFlight_v1_vs_v2`
- Select Test Case: `Valid_Flight_AA123`
- Review differences side-by-side

## 🔍 Common Use Cases

### 1. Regression Testing
Test that existing functionality still works after changes.

### 2. Breaking Change Detection
Identify if response structure changed unexpectedly.

### 3. Performance Comparison
Compare response times between old and new APIs.

### 4. Data Validation
Ensure data accuracy across API versions.

### 5. Error Handling
Test that error responses are consistent or improved.

## 🛠️ Troubleshooting

### Issue: Can't connect to API
**Solution**: 
- Check API URL is correct
- Verify authentication token
- Test with curl first: `curl -H "Authorization: Bearer TOKEN" API_URL`

### Issue: JSON parsing error
**Solution**:
- Validate JSON syntax at jsonlint.com
- Ensure proper quotes and commas
- Check for trailing commas

### Issue: Database locked
**Solution**:
```bash
# Stop application
sudo systemctl stop api-comparator
# Remove database lock
rm data/api_tests.db-journal
# Restart
sudo systemctl start api-comparator
```

## 📊 Best Practices

### Test Case Naming
✅ Good: `Valid_Flight_AA123_Nov12`  
❌ Bad: `test1`, `x`, `asdf`

### Payload Organization
- Use consistent formatting
- Group related tests
- Document expected results

### Version Control
- Commit test configurations
- Tag stable test suites
- Document API changes

## 🔒 Security Tips

1. **Never commit tokens** to git
2. **Rotate credentials** regularly
3. **Restrict IP access** in Security Groups
4. **Use HTTPS** in production
5. **Enable authentication** for Streamlit
6. **Backup database** regularly

## 📈 Advanced Features

### Batch Testing
Create multiple test cases and run them sequentially.

### Custom Headers
Add custom headers in API configuration:
```json
{
  "type": "bearer",
  "token": "your-token",
  "custom_headers": {
    "X-Request-ID": "123",
    "X-Custom-Header": "value"
  }
}
```

### Query Parameters
For GET requests, use format: `param1=value1&param2=value2`

## 📞 Useful Commands

```bash
# Check logs
sudo journalctl -u api-comparator -f

# Restart service
sudo systemctl restart api-comparator

# View database
sqlite3 data/api_tests.db "SELECT * FROM api_configs;"

# Backup database
cp data/api_tests.db backup_$(date +%Y%m%d).db

# Update application
git pull  # if using git
pip install -r requirements.txt --upgrade
sudo systemctl restart api-comparator
```

## 🎯 Pro Tips

1. **Use descriptive test names** - Future you will thank you
2. **Test edge cases** - Empty strings, nulls, large numbers
3. **Document assumptions** - What should stay the same?
4. **Compare incrementally** - Don't change everything at once
5. **Keep old tests** - Historical data is valuable
6. **Automate when possible** - Consider CI/CD integration

---

**Happy Testing! 🚀**
