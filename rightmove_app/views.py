import io
import zipfile
import pandas as pd
from io import BytesIO
from .right_move import main
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    """Home page view class"""
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        """Handles get requests to '/'"""
        return render(request, 'home.html')

    def post(self, request, *args, **kwargs):
        """Handles POST requests to '/'"""

        current_time = datetime.now().strftime('%d%m%Y_%H%M%S')

        if request.method == 'POST':
            # Get the URL from the form submission
            url = request.POST.get('url')

            try:
                # Call main function to scrape data
                pdf_content, data = main(url)

                if not pdf_content:
                    return render(request, 'home.html', {'error_message': f'Failed to process URL: {url}'})

                # Generate filenames with current time
                pdf_filename = f"property_data_{current_time}.pdf"
                excel_filename = f"property_data_{current_time}.xlsx"

                # Create PDF file response
                pdf_response = HttpResponse(pdf_content, content_type='application/pdf')
                pdf_response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'

                # Generate Excel file from data
                df = pd.DataFrame(data)
                excel_buffer = BytesIO()
                df.to_excel(excel_buffer, index=False)

                # Create Excel file response
                excel_response = HttpResponse(excel_buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                excel_response['Content-Disposition'] = f'attachment; filename="{excel_filename}"'

                # Zip both files
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.writestr(pdf_filename, pdf_content)
                    zipf.writestr(excel_filename, excel_buffer.getvalue())

                zip_filename = f"property_data_{current_time}.zip"
                # Create response for the zip file
                zip_response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
                zip_response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

                # Clean up temporary resources
                excel_buffer.close()

                return zip_response

            except Exception as e:
                return render(request, 'home.html', {'error_message': f'Error processing URL {url}: {e}'})

