# !/bin.sh

for i in $(seq 1000 1 1009)
do
   echo "Dumping s"$i
   sudo ovs-ofctl dump-flows s$i &> s$i".rule"
done
