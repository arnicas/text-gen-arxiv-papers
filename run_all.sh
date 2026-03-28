
python scrape.py
wait
python build_pages.py
wait
git add _data
wait
git add categories
wait
today=$(date +%Y-%m-%d)
git commit -m "update $today"
wait
git push origin main
echo "done with $today."