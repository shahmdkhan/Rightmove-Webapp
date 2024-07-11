import pandas as pd
from .right_move import main
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

current_time = datetime.now().strftime('%d%m%Y %H%M%S')


class HomePageView(TemplateView):
    """Home page view class"""
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        """Handles get requests to '/'"""
        return render(request, 'home.html')

    def post(self, request, *args, **kwargs):
        """Handles POST requests to '/'"""
        if request.method == 'POST':
            # Get the URL from the form submission
            url = request.POST.get('url')

            try:
                # Call main function to scrape data
                pdf_content = main(url)

                if not pdf_content:
                    return render(request, 'home.html', {'error_message': f'Failed to process URL: {url}'})

                # Generate filename with current time
                filename = f"property_data_{current_time}.pdf"

                # Set response content type
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'

                return response

            except Exception as e:
                return render(request, 'home.html', {'error_message': f'Error processing URL {url}: {e}'})


