source .env

tau2 run \
--domain airline \
--agent-llm gpt-4.1 \
--user-llm gpt-4.1 \
--num-trials 3 \
--max-concurrency 50 \
--max-steps 200 \
# --agent-llm-args '{"api_base": "'"$AGENT_BASE_URL"'", "budget": 1, "return_response_only": false, "use_router": true, "use_verifier": false, "verifier_budget": 3, "router_max_budget": 4}' 
# --task-ids 1 