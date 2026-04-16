from services.search_service import search_schemes
from services.eligibility_service import (
    check_eligibility,
    get_missing_documents,
    compute_readiness,
)

def process_query(query, user):
    results = search_schemes(query)
    
    print(f"Processing query: '{query}' - Found {len(results)} unique scheme(s)")

    final_output = []

    for scheme in results:
        eligible, reason = check_eligibility(user, scheme)

        missing = get_missing_documents(user["documents"], scheme.get("documents", ""))

        readiness = compute_readiness(user["documents"], scheme.get("documents", ""))

        # Ensure clean output with all required fields
        output_item = {
            "scheme_name": scheme.get("scheme_name"),
            "eligibility": {
                "status": eligible,
                "reason": reason
            },
            "readiness_score": readiness,
            "missing_documents": missing
        }
        
        final_output.append(output_item)

    return {
        "query": query,
        "results": final_output
    }