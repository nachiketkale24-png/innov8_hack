def check_eligibility(user, scheme):
    # Default response
    eligible = True
    reason = "Eligible"

    # Income check
    income_limit = scheme.get("income_limit")
    user_income = user.get("income")
    if income_limit is not None and user_income is not None and user_income > income_limit:
        return False, "Income exceeds limit"

    # Occupation check - flexible matching
    occupation = scheme.get("occupation", "any")
    user_occupation = user.get("occupation", "")
    
    # Normalize to lowercase for comparison
    occupation_lower = str(occupation).lower().strip()
    user_occupation_lower = str(user_occupation).lower().strip()
    
    # If scheme requires any occupation, always allow
    if occupation_lower != "any" and occupation_lower != "":
        # Check if it's a list of occupations (comma or semicolon separated)
        allowed_occupations = [occ.strip() for occ in occupation_lower.replace(";", ",").split(",")]
        
        # User occupation must be in the list of allowed occupations
        if user_occupation_lower not in allowed_occupations:
            return False, "Occupation mismatch"

    return eligible, reason


def get_missing_documents(user_docs, required_docs):
    # Handle empty, None, or NaN required_docs
    if not required_docs or (isinstance(required_docs, float)):
        return []
    
    required_str = str(required_docs).strip()
    if not required_str or required_str.lower() == "nan":
        return []
    
    required = [doc.strip() for doc in required_str.split(";") if doc.strip()]
    missing = [doc for doc in required if doc not in user_docs]
    return missing


def compute_readiness(user_docs, required_docs):
    # Handle empty, None, or NaN required_docs
    if not required_docs or (isinstance(required_docs, float)):
        return 100
    
    required_str = str(required_docs).strip()
    if not required_str or required_str.lower() == "nan":
        return 100
    
    required = [doc.strip() for doc in required_str.split(";") if doc.strip()]

    if len(required) == 0:
        return 100

    available = len([doc for doc in required if doc in user_docs])
    
    # Safe division - prevent division by zero
    if len(required) == 0:
        return 100
    
    readiness = int((available / len(required)) * 100)
    return max(0, min(100, readiness))  # Ensure value is between 0-100