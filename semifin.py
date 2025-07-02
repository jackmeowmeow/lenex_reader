#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  2 16:44:39 2025

@author: giacomogatti
"""

import xml.etree.ElementTree as ET
import os

#Just to see where we are working, sometimes I forgot the folder Im working in
print("Current directory:", os.getcwd())

def read_lenex_file_event(lenex_filename):
    """Read Lenex file and extract event information"""
    try:
        tree = ET.parse(lenex_filename)
        root = tree.getroot()
        
        event_data = []
        
        for event in root.findall('.//EVENT'):
            id_event = event.get('eventid', '')
            gender_event = event.get('gender','')
            name_event = event.find('SWIMSTYLE')
            
            if name_event is not None:
                distance_event = name_event.get('distance', '')
                stroke_event = name_event.get('stroke','').title()
                name = f'{distance_event}m {stroke_event} {gender_event}'.strip()
                
                if id_event and name:
                    event_data.append({
                        'id_event': id_event,
                        'gender_event': gender_event,
                        'event_name': name
                    })
                
        return event_data
        
    except FileNotFoundError:
        print(f"Error: Lenex file '{lenex_filename}' not found.")
        return []
    except ET.ParseError:
        print(f"Error: Could not parse '{lenex_filename}'. Make sure it's a valid XML/Lenex file.")
        return []
    except Exception as e:
        print(f"Error reading Lenex file: {e}")
        return []
    
    
# IMPROVE: find how in LENEX are stored different rounds (heats, semifinals, final) and store it
def read_lenex_file_results(lenex_filename, event_data):
    """Read Lenex file and extract results for each event"""
    try:
        tree = ET.parse(lenex_filename)
        root = tree.getroot()
        
        all_event_results = []
        
        for event in event_data:
            event_id = event['id_event']
            event_result = []
            
            # Find all clubs
            for club in root.findall('.//CLUB'):
                nationality = club.get('nation', '')
                
                # Find all athletes in this club
                for athlete in club.findall('.//ATHLETE'):
                    first_name = athlete.get('firstname', '')
                    last_name = athlete.get('lastname', '').title()
                    full_name = f"{first_name} {last_name}".strip()
                    
                    # Find all results for this athlete in the current event
                    for result in athlete.findall(f'.//RESULT[@eventid="{event_id}"]'):
                        time_str = result.get('swimtime', '')
                        
                        if time_str:
                           # Convert time format from hh:mm:ss.dd to mm:ss.dd
                           try:
                               parts = time_str.split(':')
                               if len(parts) == 3:  # hh:mm:ss.dd
                                   hh, mm, ss_dd = parts
                                   # Combine hours and minutes (60*hh + mm)
                                   total_minutes = int(hh)*60 + int(mm)
                                   new_time = f"{total_minutes}:{ss_dd}"
                               elif len(parts) == 2:  # mm:ss.dd (already correct)
                                   new_time = time_str
                               else:  # unknown format
                                   new_time = time_str
                           except:
                               new_time = time_str  # fallback to original if conversion fails
                               
                        lane = result.get('lane', '')
                        heat = result.get('heat', '')
                        
                        if new_time and lane and heat:
                            event_result.append({
                                'name': full_name,
                                'nationality': nationality,
                                'time': new_time,
                                'lane': lane,
                                'heat': heat
                            })
            
            # Sort results by time (fastest first)
            event_result.sort(key=lambda x: x['time'])
            all_event_results.append(event_result)
                
        return all_event_results
        
    except FileNotFoundError:
        print(f"Error: Lenex file '{lenex_filename}' not found.")
        return []
    except ET.ParseError:
        print(f"Error: Could not parse '{lenex_filename}'. Make sure it's a valid XML/Lenex file.")
        return []
    except Exception as e:
        print(f"Error reading Lenex file: {e}")
        return []
    
#IMPROVE: we can generate different tables if we know the difference between heats, semis and final
def create_content_with_swimmers(result_data, event_data):
    """Create wikitable content from swimmer data"""
    content = ''
    
    if not result_data or not event_data:
        content += 'No data found in the Lenex file.\n'
        return content
    
    for i, (event, results) in enumerate(zip(event_data, result_data), 1):
        content += f'=== Event {i}: {event["event_name"]} ===\n'
        content += f'Event ID: {event["id_event"]}\n\n'
        
        content += '{| class="wikitable sortable" style="text-align:center"\n'
        content += '|-\n'
        content += '! Posizione !! Batteria !! Corsia !! Atleta !! Nazionalità !! Tempo !! Note\n'
        
        for pos, result in enumerate(results, 1):
            content += '|-\n'
            content += f'| {pos} '
            content += f'|| {result["heat"]} '
            content += f'|| {result["lane"]} '
            content += f'||align=left|[[{result["name"]}]] '
            content += '|| align=left|{{'
            content += f'{result["nationality"]}'
            content += '}}'
            content += f'|| {result["time"]} '
            content += '|| \n'
        
        content += '|}\n\n'
        
    return content

 
def main():
    lenex_filename = input("Enter Lenex filename (e.g., 'results.lxf'): ").strip()
    
    if not lenex_filename:
        print("No filename provided. Exiting...")
        return
    
    print(f"Reading Lenex file: {lenex_filename}")
   
    event_data = read_lenex_file_event(lenex_filename)
    if not event_data:
        print("No event data found in the file.")
        return
    
    results_data = read_lenex_file_results(lenex_filename, event_data)
    if not results_data:
        print("No results data found in the file.")
        return
    
    content = create_content_with_swimmers(results_data, event_data)
    
    output_filename = "swimming_results.txt"
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Results written to '{output_filename}' successfully!")
    print(f"Processed {len(event_data)} events with {sum(len(r) for r in results_data)} total results.")

if __name__ == "__main__":
    main()