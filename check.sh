for r in eu-central-1 eu-central-2 eu-west-1 eu-west-2 eu-west-3 eu-south-1 eu-south-2 eu-north-1; do
  echo "Scanning region: $r"
  aws cloudformation list-stack-sets --region "$r" \
    --query "Summaries[?contains(StackSetName, 'ControlTower')].StackSetName" --output text
done
