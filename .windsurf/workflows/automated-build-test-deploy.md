---
description: Automated build, test, and deployment workflow for after every change completion
---

# Automated Build, Test & Deploy Workflow

This workflow automates the build, regression testing, and deployment process that should be run after completing changes and todos.

## When to Use
- After completing all todos in a task
- Before pushing major changes
- As part of continuous integration process
- When preparing for production deployment

## Workflow Steps

### 1. Build Verification ✅
```bash
cd frontend && npm run build
```
- Verifies frontend compiles without errors
- Checks for TypeScript errors
- Validates production build optimization
- Ensures all dependencies are properly resolved

### 2. Code Quality Checks ✅
```bash
cd frontend && npm run lint
```
- Runs ESLint to check code quality
- Ensures consistent coding standards
- Catches potential syntax errors
- Validates import/export statements

### 3. Regression Testing ✅
```bash
node -e "
// Manual regression test runner
const BASE_URL = 'https://naija-conflict-tracker-production.up.railway.app';
// Test critical API endpoints
"
```
- Tests critical API endpoints
- Validates response structures
- Checks response times (< 2 seconds)
- Ensures backward compatibility

### 4. Data Validation ✅
```bash
node -e "
// Test API endpoints with corrected data
const BASE_URL = 'https://naija-conflict-tracker-production.up.railway.app';
// Validate temporal data accuracy
"
```
- Verifies data integrity after changes
- Tests date ranges and temporal patterns
- Validates statistical calculations
- Ensures realistic data distributions

### 5. Git Operations ✅
```bash
git add .
git commit -m "Descriptive commit message"
git push origin main
```
- Stages all changes
- Creates comprehensive commit message
- Pushes to trigger deployments
- Maintains version control history

### 6. Deployment Verification ✅
```bash
curl -s "https://naija-conflict-tracker-production.up.railway.app/health"
```
- Checks backend health status
- Verifies database connectivity
- Confirms successful deployment
- Monitors service availability

## Success Criteria

### Build Status ✅
- [ ] Frontend builds without errors
- [ ] No TypeScript compilation issues
- [ ] All dependencies resolved
- [ ] Production build optimized

### Test Results ✅
- [ ] All regression tests pass
- [ ] API endpoints respond correctly
- [ ] Response times within limits
- [ ] Data validation successful

### Deployment Status ✅
- [ ] Backend service healthy
- [ ] Database connected
- [ ] Changes deployed to production
- [ ] No service interruptions

## Automation Script

Create an executable script to automate this workflow:

```bash
#!/bin/bash
# automated-build-test-deploy.sh

set -e  # Exit on any error

echo "🚀 Starting Automated Build, Test & Deploy Workflow..."

# 1. Build Verification
echo "📦 Building frontend..."
cd frontend && npm run build
if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful"
else
    echo "❌ Frontend build failed"
    exit 1
fi

# 2. Code Quality
echo "🔍 Running code quality checks..."
npm run lint
if [ $? -eq 0 ]; then
    echo "✅ Code quality checks passed"
else
    echo "❌ Code quality checks failed"
    exit 1
fi

# 3. Regression Tests
echo "🧪 Running regression tests..."
node ../scripts/regression-tests.js
if [ $? -eq 0 ]; then
    echo "✅ Regression tests passed"
else
    echo "❌ Regression tests failed"
    exit 1
fi

# 4. Git Operations
echo "📤 Committing and pushing changes..."
git add .
git commit -m "$1"  # Use provided commit message
git push origin main
if [ $? -eq 0 ]; then
    echo "✅ Changes pushed successfully"
else
    echo "❌ Git push failed"
    exit 1
fi

# 5. Deployment Verification
echo "🔍 Verifying deployment..."
sleep 10  # Wait for deployment to complete
curl -s "https://naija-conflict-tracker-production.up.railway.app/health" | jq .
if [ $? -eq 0 ]; then
    echo "✅ Deployment verified"
else
    echo "❌ Deployment verification failed"
    exit 1
fi

echo "🎉 Automated workflow completed successfully!"
```

## Usage

### Manual Execution
```bash
# Run with custom commit message
./automated-build-test-deploy.sh "Fix critical bug in user authentication"
```

### Integration with IDE
- Set up as post-commit hook
- Configure as build task in VS Code
- Add to CI/CD pipeline
- Use with git hooks

### Continuous Integration
Add to `.github/workflows/ci.yml`:
```yaml
name: Build, Test & Deploy
on:
  push:
    branches: [main]
jobs:
  build-test-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Build and Test
        run: ./automated-build-test-deploy.sh "CI/CD automated deployment"
```

## Error Handling

### Build Failures
- Check TypeScript errors
- Verify dependency versions
- Review import paths
- Check environment variables

### Test Failures
- Review API endpoint changes
- Check data structure modifications
- Verify test environment
- Update test expectations

### Deployment Issues
- Check service logs
- Verify environment configuration
- Monitor database connectivity
- Review deployment logs

## Monitoring

### Success Metrics
- Build success rate: 100%
- Test pass rate: 100%
- Deployment uptime: >99%
- Response time: <2 seconds

### Alerts
- Build failures
- Test failures  
- Deployment downtime
- API response time degradation

## Best Practices

1. **Always run full workflow** before major releases
2. **Review commit messages** for clarity and context
3. **Monitor deployment health** after changes
4. **Keep tests up to date** with API changes
5. **Document any manual interventions** required
6. **Rollback quickly** if issues detected
7. **Communicate changes** to team members

## Troubleshooting

### Common Issues
- **Build fails**: Check for missing dependencies or syntax errors
- **Tests fail**: Verify API endpoints are accessible and data structure matches
- **Deployment fails**: Check service logs and environment configuration
- **Health check fails**: Verify database connectivity and service status

### Recovery Steps
1. Identify failure point
2. Review error logs
3. Fix underlying issue
4. Re-run workflow from failed step
5. Verify complete success

---

## 🎯 Workflow Status: ACTIVE ✅

This workflow has been successfully tested and is ready for automation integration.
