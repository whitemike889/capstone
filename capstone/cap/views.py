from django.http import HttpResponse
from django.shortcuts import render

from cap.models import VolumeMetadata, TrackingToolLog
from collections import defaultdict
import csv

def index(request):
    return render(request, "index.html")


def events(request):

    """
    returns a csv report where each row contains all of the log entries for a volume, 
    organized by process step
    """

    #These are all the process steps we ended up using in production
    psteps = [ 'Prqu', 'Preq', 'Prec', 'Pana', 'Ppro', 'Pos', 'Pbat', 'Phsc', 'Pcons', 'Psca', 'Psea', 'Pwor', 'Pprc', 'Pss1', 'Ppre', 'Pacm', 'Pres', 'Pret', 'PdisLewis', 'Pmey', 'Pugv', 'Dqac', 'Dclr', 'Ddup', 'Dire', 'Dqas', 'Dx2v', 'Drcp', 'Drcs', 'misc' ]
    v = TrackingToolLog.objects.order_by("bar_code")

    # each row in the table is a log entry. Ones with pstep_id set are major
    # steps in our production process.
    event_matrix = {}
    for event in v:
        if event.bar_code not in event_matrix:
            event_matrix[event.bar_code] = {}

        if event.pstep_id is not None and event.pstep_id is not '':
            if event.pstep_id not in event_matrix[event.bar_code]:
                event_matrix[event.bar_code][event.pstep_id] = str(event.created_at)
            else:
                event_matrix[event.bar_code][event.pstep_id] = str(event.created_at) + ", " + event_matrix[event.bar_code][event.pstep_id]
        else:
            entry = str(event.created_at) + ": " + "'" + str(event.type) + "'"
            if 'misc' not in event_matrix[event.bar_code]:
                event_matrix[event.bar_code]['misc'] = entry
            else:
                event_matrix[event.bar_code]['misc'] = entry + ", " + event_matrix[event.bar_code]['misc']


    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="output.csv"'

    # write the matrix out to a CSV file
    writer = csv.writer(response)
    writer.writerow(['bar code' ] + psteps)

    for row in event_matrix:
        outputrow = []
        outputrow.append(row)
        for step in psteps:
            if step in event_matrix[row]:
                outputrow.append(event_matrix[row][step])
            else:
                outputrow.append('')
        writer.writerow(outputrow)

    return response