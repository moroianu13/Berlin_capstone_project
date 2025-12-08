#!/bin/bash
# Simple monitoring script for Berlin RentWise

echo "=== Berlin RentWise Health Check ==="
echo "Time: $(date)"
echo ""

# Check app status
echo "App Status:"
flyctl status -a berlin-rentwise

echo ""
echo "Recent Logs (last 50 lines):"
flyctl logs -a berlin-rentwise --limit 50

echo ""
echo "Machine Metrics:"
flyctl machine list -a berlin-rentwise

echo ""
echo "=== End Health Check ==="
