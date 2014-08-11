# !/bin.sh

for i in $(seq 2001 1 2240)
do
   echo "Dumping s"$i
   sudo ovs-ofctl dump-flows s$i &> s$i".rule"
done
