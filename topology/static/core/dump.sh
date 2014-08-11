# !/bin.sh

for i in $(seq 1 1 13)
do
   echo "Dumping s"$i
   sudo ovs-ofctl dump-flows s$i &> s$i".rule"
done
