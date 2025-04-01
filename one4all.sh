#!/bin/bash

# Script à exécuter toutes les 22 heures

while true
do
    echo "[$(date)] Lancement du scan..."
    python3 check_links_report.py
    echo "[$(date)] Scan terminé. Attente 22h..."
    sleep $((22 * 60 * 60))
done
