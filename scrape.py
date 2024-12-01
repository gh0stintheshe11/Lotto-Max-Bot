import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from time import sleep
import json
import re

YEAR_URL = "https://www.lottomaxnumbers.com/numbers/{year}"

DETAIL_URL = "https://www.lottomaxnumbers.com/numbers/lotto-max-result-{date}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def extract_open_data(year):
    """Extract all lottery draw dates for a given year"""
    url = YEAR_URL.format(year=year)

    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the table with class "archiveResults mobFormat"
        table = soup.find("table", {"class": "archiveResults mobFormat"})

        dates = []

        # Check if table exists
        if table and table.find("tbody"):
            # Iterate through each row in the table body
            for row in table.find("tbody").find_all("tr"):
                # Skip rows that don't contain lottery results
                if not row.find("ul", {"class": "balls"}):
                    continue

                # Extract date
                date_cell = row.find("td", {"class": "noBefore colour"})
                if date_cell and date_cell.find("a"):
                    date_str = date_cell.find("a").get_text(strip=True)
                    # Convert date string to proper format (MM-DD-YYYY)
                    try:
                        date_obj = datetime.strptime(date_str, "%B %d %Y")
                        formatted_date = date_obj.strftime("%m-%d-%Y")
                        dates.append(formatted_date)
                    except ValueError as e:
                        print(f"Error parsing date {date_str}: {e}")

        print(f"Found {len(dates)} dates for year {year}")
        return dates

    except Exception as e:
        print(f"Error extracting dates for year {year}: {e}")
        return []


def get_all_dates(start_year=2009, end_year=2024):
    """Get all lottery dates from start_year to end_year"""
    all_dates = []

    for year in range(start_year, end_year + 1):
        print(f"\nExtracting dates for {year}...")
        year_dates = extract_open_data(year)
        all_dates.extend(year_dates)
        sleep(1)  # Be nice to the server

    return all_dates


def extract_main_draw(soup):
    try:
        main_result = soup.find("div", class_="mainResult lottoMax green")
        if not main_result:
            print("Could not find main result section")
            return None

        # Draw date
        date_div = main_result.find("div", class_="date")
        date = date_div.text.strip() if date_div else ""

        # Main numbers and bonus - add more error checking
        main_numbers = []
        bonus_number = None
        balls_ul = main_result.find("ul", class_="balls")
        if balls_ul:
            for ball in balls_ul.find_all("li", class_="ball"):
                if not ball:  # Skip if ball is None
                    continue
                if "bonus-ball" in ball.get("class", []):
                    bonus_number = ball.text.strip()
                else:
                    main_numbers.append(ball.text.strip())

        # Jackpot and Winners info
        info_boxes = main_result.find_all("div", class_="box")
        jackpot = ""
        total_winners = ""
        if len(info_boxes) >= 2:
            jackpot_div = info_boxes[0].find("div", class_="text")
            winners_div = info_boxes[1].find("div", class_="text")
            jackpot = jackpot_div.text.strip() if jackpot_div else ""
            total_winners = winners_div.text.strip() if winners_div else ""

        return {
            "draw_date": date,
            "main_numbers": main_numbers,
            "bonus_number": bonus_number,
            "jackpot": jackpot,
            "total_winners": total_winners,
        }
    except Exception as e:
        print(f"Error in extract_main_draw: {str(e)}")
        return None


def extract_max_millions(soup):
    """Extract all Max Millions numbers and details"""
    try:
        max_millions = []
        max_millions_div = soup.find("div", class_="maxMillionsResultsWrap")
        
        if max_millions_div:
            # Method 1: Count divs
            div_count = len(max_millions_div.find_all("div", class_="maxMillionResults"))
            
            # Method 2: Get actual results
            for result in max_millions_div.find_all("div", class_="maxMillionResults"):
                numbers = []
                for ball in result.find_all("li", class_="ball"):
                    numbers.append(ball.text.strip())
                    
                # Get winner info if available
                winner_div = result.find("div", class_="winnerInfo")
                winner_info = winner_div.text.strip() if winner_div else ""
                
                if numbers:  # Only add if we found numbers
                    max_millions.append({
                        "numbers": numbers,
                        "winner_info": winner_info
                    })
            
            results_count = len(max_millions)
            
            # Method 3: Try to find count in text (fallback)
            if div_count != results_count:
                # Look for text like "There were 9 Max Millions prizes"
                text_content = max_millions_div.get_text()
                import re
                number_matches = re.findall(r'(\d+)\s+Max\s+Millions', text_content, re.IGNORECASE)
                if number_matches:
                    text_count = int(number_matches[0])
                    print(f"Warning: Count mismatch - Divs: {div_count}, Results: {results_count}, Text: {text_count}")
                    # Use the text count if it's larger than what we found
                    if text_count > results_count:
                        return {
                            "count": str(text_count),
                            "results": max_millions
                        }
            
            # If counts match or no text count found, use the results count
            return {
                "count": str(results_count),
                "results": max_millions
            }
        
        return {"count": "0", "results": []}
        
    except Exception as e:
        print(f"Error in extract_max_millions: {str(e)}")
        return {"count": "0", "results": []}


def extract_prize_breakdown(soup):
    try:
        breakdown_table = soup.find("table", class_="tableBreakdown")
        prize_tiers = []

        if breakdown_table and breakdown_table.find("tbody"):
            for row in breakdown_table.find("tbody").find_all("tr"):
                if "Totals" in row.text:
                    continue

                try:
                    tier = {
                        "match_type": row.find("strong").text.strip() if row.find("strong") else "",
                        "prize_per_winner": row.find("td", {"data-title": "Prize Per Winner"}).text.strip() if row.find("td", {"data-title": "Prize Per Winner"}) else "",
                        "winners": row.find("td", {"data-title": "Winners"}).text.strip() if row.find("td", {"data-title": "Winners"}) else "",
                        "prize_fund": row.find("td", {"data-title": "Prize Fund"}).text.strip() if row.find("td", {"data-title": "Prize Fund"}) else "",
                    }
                    prize_tiers.append(tier)
                except Exception as e:
                    print(f"Error processing prize tier row: {str(e)}")
                    continue

        return prize_tiers
    except Exception as e:
        print(f"Error in extract_prize_breakdown: {str(e)}")
        return []


def extract_statistics(soup):
    try:
        stats_box = soup.find("div", class_="prizeStatsBox")
        stats = {}

        if stats_box:
            for box in stats_box.find_all("div", class_="box"):
                try:
                    title_div = box.find("div", class_="title")
                    stat_div = box.find("div", class_="stat")
                    small_stat_div = box.find("div", class_="statSmall")

                    if title_div and stat_div:
                        title = title_div.text.strip()
                        stat = stat_div.text.strip()
                        
                        # Handle Tickets Sold and Total Sales
                        if title == "Tickets Sold":
                            # Extract total sales from small stat if it exists
                            if small_stat_div:
                                sales_text = small_stat_div.text.strip()
                                sales_match = re.search(r'\$[\d,]+', sales_text)
                                if sales_match:
                                    stats["Total Sales"] = {"main_stat": sales_match.group(0)}
                            stats[title] = {"main_stat": stat}
                            continue

                        # Format Winning Ratio as percentage
                        if title == "Winning Ratio":
                            numbers = re.findall(r'\d+', stat)
                            if len(numbers) >= 2:
                                ratio = (float(numbers[0]) / float(numbers[1])) * 100
                                stats[title] = {"main_stat": f"{ratio:.1f}%"}
                            continue
                        
                        # Handle Max Millions for next draw
                        if title == "Max Millions for the next draw:":
                            numbers = re.findall(r'\d+', stat)
                            stats[title] = {"main_stat": numbers[0] if numbers else "0"}
                            continue

                        # For all other stats
                        stat_dict = {"main_stat": stat}
                        if small_stat_div and small_stat_div.text.strip():
                            stat_dict["additional_info"] = small_stat_div.text.strip()
                        stats[title] = stat_dict

                except Exception as e:
                    print(f"Error processing stats box: {str(e)}")
                    continue

        return stats
    except Exception as e:
        print(f"Error in extract_statistics: {str(e)}")
        return {}


def extract_provincial_stats(soup):
    try:
        province_table = soup.find("table", class_="provinceStats")
        provinces = []

        if province_table and province_table.find("tbody"):
            for row in province_table.find("tbody").find_all("tr"):
                try:
                    cells = row.find_all("td")
                    if len(cells) >= 3:
                        province = {
                            "province": cells[0].text.strip(),
                            "winners": cells[1].text.strip(),
                            "amount_won": cells[2].text.strip(),
                        }
                        provinces.append(province)
                except Exception as e:
                    print(f"Error processing province row: {str(e)}")
                    continue

        return provinces
    except Exception as e:
        print(f"Error in extract_provincial_stats: {str(e)}")
        return []


def extract_all_lottery_data(html_content):
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        
        main_draw = extract_main_draw(soup)
        if not main_draw:
            print("Failed to extract main draw data")
            return None

        return {
            "main_draw": main_draw,
            "max_millions": extract_max_millions(soup),
            "prize_breakdown": extract_prize_breakdown(soup),
            "statistics": extract_statistics(soup),
            "provincial_stats": extract_provincial_stats(soup),
        }
    except Exception as e:
        print(f"Error in extract_all_lottery_data: {str(e)}")
        return None


def scrape_detail_page(date, max_retries=3):
    """Scrape the detail page for a specific date with retries"""
    url = DETAIL_URL.format(date=date)
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 404:
                print(f"No results found for {date}")
                return None
            elif response.status_code != 200:
                print(f"Got status code {response.status_code} for {date}")
                sleep(2)  # Wait before retry
                continue
                
            data = extract_all_lottery_data(response.text)
            if data:
                data['date'] = date
                data['url'] = url
                return data
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {date}: {str(e)}")
            sleep(2)  # Wait before retry
            
    print(f"Failed to scrape {date} after {max_retries} attempts")
    return None


def main():
    # First get all dates
    print("Getting all lottery draw dates...")
    all_dates = get_all_dates(2009, 2024)
    print(f"\nFound total of {len(all_dates)} draw dates")
    
    # Try to load existing results
    try:
        with open('lottery_results_final.json', 'r') as f:  # Changed from partial to final
            existing_results = json.load(f)
            print(f"\nLoaded {len(existing_results)} existing results")
            
        # Find new dates to scrape
        existing_dates = set(r['date'] for r in existing_results)
        new_dates = [d for d in all_dates if d not in existing_dates]
        print(f"\nNew dates to scrape: {len(new_dates)}")
        
        if not new_dates:
            print("No new draws to scrape. Exiting...")
            return
        
        # Scrape only new dates
        print("\nScraping new draws...")
        for i, date in enumerate(new_dates, 1):
            print(f"\nScraping {date} ({i}/{len(new_dates)})...")
            result = scrape_detail_page(date)
            if result:
                existing_results.append(result)
            sleep(1)
        
        # Save updated results
        print("\nSaving updated results...")
        with open('lottery_results_final.json', 'w') as f:
            json.dump(existing_results, f, indent=2)
        
    except FileNotFoundError:
        print("\nNo existing results found, starting fresh")
        # If no existing file, scrape all dates
        all_results = []
        for i, date in enumerate(all_dates, 1):
            print(f"\nScraping {date} ({i}/{len(all_dates)})...")
            result = scrape_detail_page(date)
            if result:
                all_results.append(result)
            sleep(1)
        
        # Save results
        print("\nSaving results...")
        with open('lottery_results_final.json', 'w') as f:
            json.dump(all_results, f, indent=2)
    
    print("\nScraping completed!")


if __name__ == "__main__":
    main()