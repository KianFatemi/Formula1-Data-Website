from django.shortcuts import render
import fastf1
import fastf1.plotting
import seaborn as sns
from matplotlib import pyplot as plt
from io import BytesIO
import base64
from django.http import JsonResponse
from django.core.cache import cache
from timple.timedelta import strftimedelta
import pandas as pd
from fastf1.core import Laps
from data.models import Race, Driver
import logging
logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'home.html')

def get_available_races(year):
    races = Race.objects.filter(year=year).values_list('name', flat=True)
    return list(races)

def get_available_drivers(year):
    drivers = Driver.objects.filter(year=year).values_list('abbreviation', flat=True)
    return list(drivers)

def error_page(request):
    error_message = 'An error has occurred.'  # Customize the error message as needed
    return render(request, 'error.html', {'message': error_message})

def laptimes_distribution(request):
    years = [2019, 2020,2021, 2022, 2023]  # List of available years

    try:
        if request.method == 'POST':
            year = request.POST.get('year')
            selected_race = request.POST.get('race')
            
            # Get the available races for the selected year
            races = get_available_races(year)

            # Load the race session
            race = fastf1.get_session(int(year), selected_race, 'R')
            race.load()

            # Get all the laps for the point finishers only
            point_finishers = race.drivers[:10]
            driver_laps = race.laps.pick_drivers(point_finishers).pick_quicklaps()
            driver_laps = driver_laps.reset_index()

            # Get the drivers' abbreviations in finishing order
            finishing_order = [race.get_driver(i)["Abbreviation"] for i in point_finishers]

            # Modify the DRIVER_COLORS palette
            driver_colors = {abv: fastf1.plotting.DRIVER_COLORS[driver] for abv, driver in fastf1.plotting.DRIVER_TRANSLATE.items()}

            # Create the figure
            fig, ax = plt.subplots(figsize=(10, 5))

            # Convert timedelta to float in seconds
            driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()
            print("----------\n", driver_laps['LapTime(s)'])
            sns.violinplot(data=driver_laps,
                        x="Driver",
                        y="LapTime(s)",
                        inner=None,
                        scale="area",
                        order=finishing_order,
                        palette=list(driver_colors.values())
                        )
            
            print("----------After\n", driver_laps)
            sns.swarmplot(data=driver_laps,
                        x="Driver",
                        y="LapTime(s)",
                        order=finishing_order,
                        hue="Compound",
                        palette=fastf1.plotting.COMPOUND_COLORS,
                        # hue_order=["SOFT", "MEDIUM", "HARD"],
                        linewidth=0,
                        size=5,
                        )

            ax.set_xlabel("Driver")
            ax.set_ylabel("Lap Time (s)")
            plt.suptitle(f"{race}")
            sns.despine(left=True, bottom=True)

            plt.tight_layout()

            # Save the plot to a base64-encoded image
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            laptimes_plot = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
        
            return render(request, 'laptimes_distribution.html', {'years': years, 'races': races, 'laptimes_plot': laptimes_plot})

    except KeyError as e:
        # Handle the KeyError exception
        error_message = f"Error: {str(e)}"
        return render(request, 'error.html', {'message': error_message})
    except ValueError as e:
        error_message = f"Error: {str(e)}"
        return render(request, 'error.html', {'message': error_message})

    return render(request, 'laptimes_distribution.html', {'years': years})

def get_races(request):
    year = request.GET.get('year')
    races = get_available_races(int(year))
    return JsonResponse({'races': races})

def get_drivers(request):
    year = request.GET.get('year')
    drivers = get_available_drivers(int(year))
    return JsonResponse({'drivers': drivers})

def speed_trace(request):
    years = [2019, 2020, 2021, 2022, 2023]   # List of available years
    races = []
    plt.switch_backend('Agg')
    try:
        if request.method == 'POST':
            year = request.POST.get('year')
            selected_race = request.POST.get('race')
            selected_driver_1 = request.POST.get('driver1')
            selected_driver_2 = request.POST.get('driver2')

            # Get the available races for the selected year
            races = get_available_races(year)
            drivers = get_available_drivers(year)

            fastf1.plotting.setup_mpl(misc_mpl_mods=False)

            session = fastf1.get_session(int(year), selected_race, 'Q')
            session.load()

            lap_driver_1 = session.laps.pick_driver(selected_driver_1).pick_fastest()
            lap_driver_2 = session.laps.pick_driver(selected_driver_2).pick_fastest()

            tel_driver_1 = lap_driver_1.get_car_data().add_distance()
            tel_driver_2 = lap_driver_2.get_car_data().add_distance()

            # Define a color palette
            color_palette = ['red', 'blue', 'green', 'orange', 'purple']

            # Assign colors to the drivers
            driver_colors = {selected_driver_1: color_palette[0], selected_driver_2: color_palette[1]}

            fig, ax = plt.subplots()
            ax.plot(tel_driver_1['Distance'], tel_driver_1['Speed'], color=driver_colors.get(selected_driver_1, 'gray'), label=selected_driver_1)
            ax.plot(tel_driver_2['Distance'], tel_driver_2['Speed'], color=driver_colors.get(selected_driver_2, 'gray'), label=selected_driver_2)

            ax.set_xlabel('Distance in m')
            ax.set_ylabel('Speed in km/h')

            ax.legend()
            plt.suptitle(f"Fastest Lap Comparison \n {session.event['EventName']} {session.event.year} Qualifying")

            # Save the plot to a base64-encoded image
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            speed_plot = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)

            return render(request, 'speed_trace.html', {'years': years, 'races': races, 'drivers': drivers, 'speed_plot': speed_plot})
        
    except KeyError as e:
        # Handle the KeyError exception
        error_message = f"Error: {str(e)}"
        return render(request, 'error.html', {'message': error_message})
    except ValueError as e:
        error_message = f"Error: {str(e)}"
        return render(request, 'error.html', {'message': error_message})
    
    return render(request, 'speed_trace.html', {'years': years, 'races': races})

def qualifying_results(request):
    years = [2019, 2020, 2021, 2022, 2023]  # List of available years

    try:

        if request.method == 'POST':
            year = request.POST.get('year')
            selected_race = request.POST.get('race')

            races = get_available_races(year)
                        
            fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None, misc_mpl_mods=False)

            session = fastf1.get_session(int(year), selected_race, 'Q')
            session.load()

            drivers = pd.unique(session.laps['Driver'])
            print(drivers)

            list_fastest_laps = list()
            for drv in drivers:
                drvs_fastest_lap = session.laps.pick_driver(drv).pick_fastest()
                list_fastest_laps.append(drvs_fastest_lap)
            fastest_laps = Laps(list_fastest_laps).sort_values(by='LapTime').reset_index(drop=True)

            pole_lap = fastest_laps.pick_fastest()
            fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']

            print(fastest_laps[['Driver', 'LapTime', 'LapTimeDelta']])

            team_colors = list()
            for index, lap in fastest_laps.iterlaps():
                identifier = lap['Team']
                if pd.notna(identifier):  # Check if the value is not NaT
                    color = fastf1.plotting.team_color(identifier)
                    team_colors.append(color)
                else:
                # Handle the case where identifier is NaT (e.g., assign a default color)
                    team_colors.append('gray')

            fig, ax = plt.subplots()
            ax.barh(fastest_laps.index, fastest_laps['LapTimeDelta'],
                    color=team_colors, edgecolor='grey')
            ax.set_yticks(fastest_laps.index)
            ax.set_yticklabels(fastest_laps['Driver'])

            ax.invert_yaxis()

            ax.set_axisbelow(True)
            ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

            lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')

            plt.suptitle(f"{session.event['EventName']} {session.event.year} Qualifying\n"
                        f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            qualifying_plot = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return render(request, 'qualifying_results.html', {'years': years, 'races': races, 'qualifying_plot': qualifying_plot})
        
    except KeyError as e:
        # Handle the KeyError exception
        error_message = f"Error: {str(e)}"
        return render(request, 'error.html', {'message': error_message})
    except ValueError as e:
        error_message = f"Error: {str(e)}"
        return render(request, 'error.html', {'message': error_message})
    
    return render(request, 'qualifying_results.html', {'years': years})

def position_changes(request):
    years = [2019, 2020, 2021, 2022, 2023]  # List of available years
    try:

        if request.method == 'POST':
            year = request.POST.get('year')
            selected_race = request.POST.get('race')

            races = get_available_races(year)
            fastf1.plotting.setup_mpl(misc_mpl_mods=False)

            session = fastf1.get_session(int(year), selected_race, 'R')
            session.load(telemetry=False, weather=False)

            fig, ax = plt.subplots(figsize=(8.0, 4.9))

            for drv in session.drivers:
                drv_laps = session.laps.pick_driver(drv)

                abb = drv_laps['Driver'].iloc[0]

                try:
                    color = fastf1.plotting.driver_color(abb)
                except KeyError:
                    color = 'gray'  # Set a default color if no mapping is found

                ax.plot(drv_laps['LapNumber'], drv_laps['Position'],
                        label=abb, color=color)

            ax.set_ylim([20.5, 0.5])
            ax.set_yticks([1, 5, 10, 15, 20])
            ax.set_xlabel('Lap')
            ax.set_ylabel('Position')

            ax.legend(bbox_to_anchor=(1.0, 1.02))
            plt.tight_layout()

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            position_plot = base64.b64encode(buffer.getvalue()).decode()
            plt.close()

            return render(request, 'position_changes.html', {'years': years, 'races': races, 'position_plot': position_plot})
        
    except KeyError as e:
        # Handle the KeyError exception
        error_message = f"Error: {str(e)}"
        return render(request, 'error.html', {'message': error_message})
    except ValueError as e:
        error_message = f"Error: {str(e)}"
        return render(request, 'error.html', {'message': error_message})

    return render(request, 'position_changes.html', {'years': years})
