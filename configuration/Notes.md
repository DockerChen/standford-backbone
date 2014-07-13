
# Generate transfer functions
* cd utils
* python generate_stanford_ip_fwd_tf.py

# Generate OpenFlow rules
* mkdir work/stanford_openflow_rules
* cd utils
* python generate_stanford_openflow_rules.py

# Deploy to mahak location
* mkdir /tmp/of_rules
* cp work/stanford_openflow_rules/* /tmp/of_rules