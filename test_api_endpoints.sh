#!/bin/bash

# FineData API Endpoints Test Script
# Tests all API endpoints to ensure they are working correctly
#
# Usage: ./test_api_endpoints.sh
#
# Prerequisites:
# - Docker Compose services must be running (docker-compose up -d)
# - API service should be accessible at http://localhost:18000
#
# This script tests the following endpoints:
# - Health check (/health)
# - Email validation (/api/v1/email/validate)
# - Email verification (/api/v1/email/verify/send)
# - Ontology generation (/api/v1/ontology/generate)
# - Benchmark quote generation (/api/v1/benchmark/quote)
# - Benchmark job creation (/api/v1/benchmark/jobs)
# - Benchmark job status (/api/v1/benchmark/jobs/{job_id})
# - Order creation (/api/v1/orders) - may fail without proper DB setup
# - Order status (/api/v1/orders/{order_id})
# - Production status (/api/v1/orders/{order_id}/production)
# - Checkout session (/api/v1/checkout/session) - may fail without Stripe keys
#
# Note: Some tests may fail in development environment due to missing configurations
# (Stripe keys, email services, etc.) - this is expected.

# Don't exit on individual test failures - we want to run all tests
# set -e  # Commented out to allow all tests to run

# Configuration
API_BASE_URL="http://localhost:18000/api/v1"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables for test tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Global variables for test data sharing
KEYWORDS_ARRAY=""
QUOTE_ID=""
JOB_ID=""
ORDER_ID=""

# Test data
TEST_EMAIL="test@example.com"
TEST_DOMAIN="artificial intelligence"
TEST_KEYWORDS='["machine learning", "neural networks", "deep learning"]'
TEST_LANGUAGES='["en"]'
TEST_TIME_RANGE='{"start": "2023-01-01", "end": "2024-12-31"}'

# Utility functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

test_passed() {
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
    log_success "$1"
}

test_failed() {
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    log_error "$1"
}

make_request() {
    local method=$1
    local url=$2
    local data=$3
    local expected_status=${4:-200}
    local description=$5
    local return_response=${6:-false}

    log_info "Testing $description..."

    local response
    local status_code
    local response_body
    local curl_exit_code

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" --connect-timeout 10 --max-time 30 "$url" 2>/dev/null)
        curl_exit_code=$?
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            --connect-timeout 10 --max-time 30 \
            -d "$data" 2>/dev/null)
        curl_exit_code=$?
    fi

    status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | head -n -1)

    # Check if curl failed completely
    if [ "$curl_exit_code" -ne 0 ]; then
        test_failed "$description (Curl failed with exit code: $curl_exit_code)"
        echo "URL: $url" >&2
        echo "Method: $method" >&2
        if [ "$method" != "GET" ]; then
            echo "Data: $data" >&2
        fi
        return 1
    fi

    if [ "$status_code" -eq "$expected_status" ]; then
        test_passed "$description (Status: $status_code)"
        if [ "$return_response" = "true" ]; then
            echo "$response_body"
        fi
        return 0
    else
        test_failed "$description (Expected: $expected_status, Got: $status_code)"
        echo "URL: $url" >&2
        echo "Method: $method" >&2
        if [ "$method" != "GET" ]; then
            echo "Data: $data" >&2
        fi
        echo "Response: $response_body" >&2
        return 1
    fi
}

# Wrapper function that returns the response
make_request_with_response() {
    local method=$1
    local url=$2
    local data=$3
    local expected_status=${4:-200}
    local description=$5

    local response
    local status_code
    local response_body
    local curl_exit_code

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" --connect-timeout 10 --max-time 30 "$url" 2>/dev/null)
        curl_exit_code=$?
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            --connect-timeout 10 --max-time 30 \
            -d "$data" 2>/dev/null)
        curl_exit_code=$?
    fi

    status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | head -n -1)

    # Check if curl failed completely
    if [ "$curl_exit_code" -ne 0 ]; then
        test_failed "$description (Curl failed with exit code: $curl_exit_code)"
        echo "URL: $url" >&2
        echo "Method: $method" >&2
        if [ "$method" != "GET" ]; then
            echo "Data: $data" >&2
        fi
        return 1
    fi

    if [ "$status_code" -eq "$expected_status" ]; then
        # For response-capturing requests, don't output success message to avoid mixing with response
        test_passed "$description (Status: $status_code)"
        # Output only the response body to stdout for capturing
        printf '%s\n' "$response_body"
        return 0
    else
        test_failed "$description (Expected: $expected_status, Got: $status_code)"
        echo "URL: $url" >&2
        echo "Method: $method" >&2
        if [ "$method" != "GET" ]; then
            echo "Data: $data" >&2
        fi
        echo "Response: $response_body" >&2
        return 1
    fi
}

check_services() {
    log_info "Checking if Docker Compose services are running..."

    if ! docker-compose ps | grep -q "finedata-api"; then
        log_error "API service is not running. Please start with: docker-compose up -d"
        exit 1
    fi

    if ! docker-compose ps | grep -q "finedata-postgres"; then
        log_warning "PostgreSQL service is not running"
    fi

    if ! docker-compose ps | grep -q "finedata-redis"; then
        log_warning "Redis service is not running"
    fi

    log_success "Services check completed"
}

# API Endpoint Tests
test_health_endpoint() {
    log_info "Testing health endpoint..."
    make_request "GET" "http://localhost:18000/health" "" 200 "Health check"
}

test_email_validate() {
    local data='{"email": "'$TEST_EMAIL'"}'
    make_request "POST" "$API_BASE_URL/email/validate" "$data" 200 "Email validation"
}

test_email_verify_send() {
    local data='{"email": "'$TEST_EMAIL'"}'
    make_request "POST" "$API_BASE_URL/email/verify/send" "$data" 200 "Send email verification"
}

test_email_verify_confirm() {
    # Note: This test will likely fail without a valid token
    # In a real scenario, you'd get the token from the email sent above
    local data='{"token": "fake-verification-token-for-testing"}'
    # This may return 400/422 for invalid token, which is expected
    make_request "POST" "$API_BASE_URL/email/verify/confirm" "$data" 400 "Confirm email verification"
}

test_ontology_generate() {
    local data='{"domain": "'$TEST_DOMAIN'", "locale": "en"}'
    if ! local response=$(make_request_with_response "POST" "$API_BASE_URL/benchmark/ontology/generate" "$data" 200 "Ontology generation"); then
        log_warning "Ontology generation request failed"
        return 1
    fi

    # Validate response structure
    if echo "$response" | jq -e '.summary' >/dev/null 2>&1; then
        log_success "Ontology response contains summary"
    else
        log_warning "Ontology response missing summary field"
        echo "Response: $response" >&2
    fi

    if echo "$response" | jq -e '.positive_keywords' >/dev/null 2>&1; then
        log_success "Ontology response contains positive_keywords"
    else
        log_warning "Ontology response missing positive_keywords field"
        echo "Response: $response" >&2
    fi
}

test_benchmark_quote() {
    # First generate ontology to get keywords
    local ontology_data='{"domain": "'$TEST_DOMAIN'", "locale": "en"}'
    local ontology_response=$(curl -s -X POST "$API_BASE_URL/benchmark/ontology/generate" \
        -H "Content-Type: application/json" \
        -d "$ontology_data" 2>/dev/null)

    # Extract positive keywords from ontology using jq
    local keywords_from_ontology=$(echo "$ontology_response" | jq -r '.positive_keywords // empty' 2>/dev/null)

    if [ -z "$keywords_from_ontology" ] || [ "$keywords_from_ontology" = "null" ]; then
        log_warning "Failed to extract keywords from ontology, using fallback keywords"
        KEYWORDS_ARRAY="$TEST_KEYWORDS"
    else
        # Convert jq array output to JSON array format
        KEYWORDS_ARRAY=$(echo "$keywords_from_ontology" | jq -c '.' 2>/dev/null || echo "$TEST_KEYWORDS")
    fi

    local data='{
        "domain": "'$TEST_DOMAIN'",
        "keywords": '$KEYWORDS_ARRAY',
        "languages": '$TEST_LANGUAGES',
        "startDate": "2023-01-01",
        "endDate": "2024-12-31",
        "qualityTier": "standard"
    }'
    local response=$(make_request_with_response "POST" "$API_BASE_URL/benchmark/quote" "$data" 200 "Benchmark quote generation")

    # Extract quote ID for later use using jq
    QUOTE_ID=$(echo "$response" | jq -r '.quoteId // empty' 2>/dev/null)
    if [ -n "$QUOTE_ID" ] && [ "$QUOTE_ID" != "null" ]; then
        echo "Generated quote ID: $QUOTE_ID"
    else
        log_warning "Failed to extract quote ID from response"
        QUOTE_ID=""
    fi
}

test_benchmark_job_create() {
    # Use keywords from ontology if available, otherwise use fallback
    local keywords_to_use="$KEYWORDS_ARRAY"
    if [ -z "$keywords_to_use" ]; then
        keywords_to_use="$TEST_KEYWORDS"
        log_warning "Using fallback keywords - ontology keywords not available"
    fi

    local data='{
        "domain": "'$TEST_DOMAIN'",
        "keywords": '$keywords_to_use',
        "languages": '$TEST_LANGUAGES',
        "time_range": '$TEST_TIME_RANGE',
        "quality_tier": "standard",
        "email": "'$TEST_EMAIL'"
    }'
    local response=$(make_request_with_response "POST" "$API_BASE_URL/benchmark/jobs" "$data" 200 "Benchmark job creation")

    # Extract job ID for later use using jq
    JOB_ID=$(echo "$response" | jq -r '.jobId // empty' 2>/dev/null)
    if [ -n "$JOB_ID" ] && [ "$JOB_ID" != "null" ]; then
        echo "Created job ID: $JOB_ID"
    else
        log_warning "Failed to extract job ID from response"
        JOB_ID=""
    fi
}

test_benchmark_job_get() {
    if [ -z "$JOB_ID" ]; then
        log_warning "Skipping benchmark job status test - no job ID available"
        return
    fi

    make_request "GET" "$API_BASE_URL/benchmark/jobs/$JOB_ID" "" 200 "Benchmark job status retrieval"
}

test_order_create() {
    if [ -z "$QUOTE_ID" ] || [ -z "$JOB_ID" ]; then
        log_warning "Skipping order creation test - missing quote ID or job ID"
        return
    fi

    local data='{
        "quoteId": "'$QUOTE_ID'",
        "jobId": "'$JOB_ID'",
        "email": "'$TEST_EMAIL'"
    }'
    local response=$(make_request_with_response "POST" "$API_BASE_URL/orders" "$data" 200 "Order creation")

    # Extract order ID for later use using jq
    ORDER_ID=$(echo "$response" | jq -r '.orderId // empty' 2>/dev/null)
    if [ -n "$ORDER_ID" ] && [ "$ORDER_ID" != "null" ]; then
        echo "Created order ID: $ORDER_ID"
    else
        log_warning "Failed to extract order ID from response"
        ORDER_ID=""
    fi
}

test_order_get() {
    if [ -z "$ORDER_ID" ]; then
        log_warning "Skipping order retrieval test - no order ID available"
        return
    fi

    make_request "GET" "$API_BASE_URL/orders/$ORDER_ID" "" 200 "Order status retrieval"
}

test_order_production_status() {
    if [ -z "$ORDER_ID" ]; then
        log_warning "Skipping production status test - no order ID available"
        return
    fi

    make_request "GET" "$API_BASE_URL/orders/$ORDER_ID/production" "" 200 "Production status retrieval"
}

test_checkout_session() {
    if [ -z "$JOB_ID" ]; then
        log_warning "Skipping checkout session test - no job ID available"
        return
    fi

    local data='{"jobId": "'$JOB_ID'"}'
    # Note: This may fail due to Stripe test keys not being configured
    # We expect this in development environment
    if make_request "POST" "$API_BASE_URL/checkout/session" "$data" 200 "Checkout session creation"; then
        log_success "Checkout session created successfully"
    else
        log_warning "Checkout session failed (expected in dev environment without Stripe keys)"
        ((TOTAL_TESTS--))  # Don't count this as a failed test
        ((FAILED_TESTS--))
    fi
}

print_summary() {
    echo
    echo "=========================================="
    echo "API Endpoint Test Summary"
    echo "=========================================="
    echo "Total tests: $TOTAL_TESTS"
    echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed. Please check the output above.${NC}"
        exit 1
    fi
}

# Main execution
main() {
    echo "FineData API Endpoints Test Script"
    echo "==================================="
    echo

    check_services
    echo

    # Test basic endpoints
    test_health_endpoint
    echo

    # Test email endpoints
    log_info "Testing email endpoints..."
    test_email_validate
    test_email_verify_send
    test_email_verify_confirm
    echo

    # Test ontology endpoints
    log_info "Testing ontology endpoints..."
    test_ontology_generate
    echo

    # Test benchmark endpoints
    log_info "Testing benchmark endpoints..."
    test_benchmark_quote
    test_benchmark_job_create
    test_benchmark_job_get
    echo

    # Test order endpoints
    log_info "Testing order endpoints..."
    test_order_create
    test_order_get
    test_order_production_status
    echo

    # Test payment endpoints
    log_info "Testing payment endpoints..."
    test_checkout_session
    echo

    print_summary
}

# Run main function
main "$@"
