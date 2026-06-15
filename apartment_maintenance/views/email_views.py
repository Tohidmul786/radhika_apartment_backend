import io
import datetime
<<<<<<< HEAD
import logging

from django.core.mail import EmailMessage, send_mail
=======

from django.core.mail import EmailMessage
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
<<<<<<< HEAD
from rest_framework.permissions import IsAdminUser, IsAuthenticated
=======
from rest_framework.permissions import IsAdminUser
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d
from rest_framework import status

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)

from apartment_maintenance.models import Flat

<<<<<<< HEAD
logger = logging.getLogger(__name__)


# ── Build Receipt PDF ─────────────────────────────────────────────────
def build_receipt_pdf_bytes(flat):
=======

def build_receipt_pdf_bytes(flat):
    """Generate the same receipt PDF as FlatReceiptPDFView, return raw bytes."""
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d
    owner    = getattr(flat, 'owner', None)
    payments = flat.payments.filter(status='completed').order_by('-payment_date')[:10]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    story  = []

    header_data = [[
        Paragraph('<b><font size=14 color="#0c1f3f">Radhika Apartment</font></b><br/>'
                  '<font size=7 color="grey">New Ganesh Nagar, Hazimalang Road, Adiwali, Kalyan (East) - 421306</font>',
                  styles['Normal']),
        Paragraph(f'<b><font size=22 color="#1a56db">RECEIPT</font></b><br/>'
                  f'<font size=8 color="grey">Date: {datetime.date.today().strftime("%d %B %Y")}</font>',
                  ParagraphStyle('R', alignment=2, parent=styles['Normal'])),
    ]]
    header_tbl = Table(header_data, colWidths=[12*cm, 6*cm])
<<<<<<< HEAD
    header_tbl.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),12)]))
=======
    header_tbl.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BOTTOMPADDING',(0,0),(-1,-1),12),
    ]))
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d
    story.append(header_tbl)
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a56db')))
    story.append(Spacer(1,16))

    sc = flat.payment_status
    bal_color = '#15803d' if sc=='paid' else '#991b1b' if sc=='overdue' else '#854d0e'

    info_data = [
        ['Flat Number', flat.flat_number, 'Wing', f'Wing {flat.wing.name}'],
        ['Floor', flat.floor.name, 'Status',
         Paragraph(f'<b><font color="{bal_color}">{sc.upper()}</font></b>', styles['Normal'])],
        ['Owner Name', owner.name if owner else 'N/A', 'Phone', owner.phone if owner else 'N/A'],
        ['Email', owner.email if owner else 'N/A', 'Monthly', f'Rs. {flat.monthly_maintenance:,.0f}'],
    ]
    info_tbl = Table(info_data, colWidths=[4*cm,6*cm,4*cm,4*cm])
    info_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1), colors.HexColor('#f0f4f8')),
        ('BACKGROUND',(2,0),(2,-1), colors.HexColor('#f0f4f8')),
        ('FONTNAME',  (0,0),(0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (2,0),(2,-1), 'Helvetica-Bold'),
        ('FONTSIZE',  (0,0),(-1,-1), 9),
        ('GRID',      (0,0),(-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING',(0,0),(-1,-1), 7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),8),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1,16))

    bal_bg = colors.HexColor('#dcfce7') if sc=='paid' else colors.HexColor('#fee2e2') if sc=='overdue' else colors.HexColor('#fef9c3')
    bal_data = [[
<<<<<<< HEAD
        Paragraph(f'<b><font size=11>Outstanding Balance</font></b><br/>'
=======
        Paragraph(f'<b><font size=11>Outstanding Balance</font></b><br/><br/>'
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d
                  f'<font size=22 color="{bal_color}"><b>Rs. {flat.total_balance:,.0f}</b></font>',
                  styles['Normal']),
        Paragraph(f'<font size=9 color="grey">Pending Months: <b>{int(flat.total_balance/flat.monthly_maintenance) if flat.total_balance>0 else 0}</b><br/>'
                  f'Monthly Charge: <b>Rs. {flat.monthly_maintenance:,.0f}</b></font>',
                  styles['Normal']),
    ]]
    bal_tbl = Table(bal_data, colWidths=[9*cm,9*cm])
    bal_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), bal_bg),
        ('GRID',(0,0),(-1,-1),0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING',(0,0),(-1,-1),12),
        ('BOTTOMPADDING',(0,0),(-1,-1),12),
        ('LEFTPADDING',(0,0),(-1,-1),14),
    ]))
    story.append(bal_tbl)
    story.append(Spacer(1,20))

    story.append(Paragraph('<b><font size=11 color="#0c1f3f">Recent Payment History</font></b>', styles['Normal']))
    story.append(Spacer(1,8))

    if payments:
        pay_headers = ['#','Date','Amount (Rs.)','Mode','Transaction ID','Received By']
        pay_data = [pay_headers]
        for i, pay in enumerate(payments,1):
            pay_data.append([
<<<<<<< HEAD
                str(i), pay.payment_date.strftime('%d/%m/%Y'), f'{pay.amount:,.0f}',
                pay.payment_mode.upper(), pay.transaction_id or '—',
=======
                str(i),
                pay.payment_date.strftime('%d/%m/%Y'),
                f'{pay.amount:,.0f}',
                pay.payment_mode.upper(),
                pay.transaction_id or '—',
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d
                pay.received_by.get_full_name() if pay.received_by else 'Admin',
            ])
        pay_tbl = Table(pay_data, colWidths=[1*cm,3.5*cm,4*cm,3*cm,4*cm,3*cm])
        pay_tbl.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0), colors.HexColor('#0c1f3f')),
            ('TEXTCOLOR', (0,0),(-1,0), colors.white),
            ('FONTNAME',  (0,0),(-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',  (0,0),(-1,-1), 8),
            ('ALIGN',     (0,0),(-1,-1), 'CENTER'),
            ('GRID',      (0,0),(-1,-1), 0.4, colors.HexColor('#e5e7eb')),
            ('TOPPADDING',(0,0),(-1,-1), 5),
            ('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#f0f9ff')]),
        ]))
        story.append(pay_tbl)
    else:
        story.append(Paragraph('<font color="grey">No payment records found.</font>', styles['Normal']))

    story.append(Spacer(1,30))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Spacer(1,8))
    story.append(Paragraph(
<<<<<<< HEAD
        '<font size=8 color="grey">This is a computer-generated receipt. For queries contact the society office.</font>',
=======
        '<font size=8 color="grey">This is a computer-generated receipt. '
        'For queries contact the society office.</font>',
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d
        ParagraphStyle('Footer', alignment=1, parent=styles['Normal'])))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def reminder_email_body(flat, owner):
    months = int(flat.total_balance / flat.monthly_maintenance) if flat.total_balance > 0 else 0
    portal_url = getattr(settings, 'FRONTEND_URL', '')
    body = f"""Dear {owner.name},

<<<<<<< HEAD
This is a friendly reminder regarding your maintenance dues for Flat {flat.flat_number}, Radhika Apartment Co-op Housing Society.

Outstanding Balance : Rs. {flat.total_balance:,.0f}
Pending Months      : {months}
Monthly Charge      : Rs. {flat.monthly_maintenance:,.0f}
=======
This is a friendly reminder regarding your maintenance dues for Flat {flat.flat_number}, Radhika Apartment.

Outstanding Balance: Rs. {flat.total_balance:,.0f}
Pending Months: {months}
Monthly Charge: Rs. {flat.monthly_maintenance:,.0f}
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d

Please clear the dues at the earliest. A detailed receipt is attached to this email for your reference.
"""
    if portal_url:
<<<<<<< HEAD
        body += f"\nYou can check your balance anytime at: {portal_url}\n"
    body += "\nThank you,\nRadhika Apartment Co-op Housing Society"
    return body


# ── TEST EMAIL — verify Gmail config is working ───────────────────────
class TestEmailView(APIView):
    """
    POST /api/reminders/test-email/
    Body: { "to_email": "youremail@gmail.com" }
    Sends a simple test email — no PDF, no flat data.
    Use this first to confirm Gmail SMTP is configured correctly.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        to_email = request.data.get('to_email', '').strip()
        if not to_email:
            return Response(
                {'error': 'Provide a "to_email" field in the request body.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Show current config (password masked)
        config_info = {
            'EMAIL_HOST':      getattr(settings, 'EMAIL_HOST', 'NOT SET'),
            'EMAIL_PORT':      getattr(settings, 'EMAIL_PORT', 'NOT SET'),
            'EMAIL_USE_TLS':   getattr(settings, 'EMAIL_USE_TLS', 'NOT SET'),
            'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', 'NOT SET'),
            'EMAIL_HOST_PASSWORD': '****' if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else 'NOT SET',
            'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET'),
        }

        try:
            send_mail(
                subject='✅ Test Email — Radhika Apartment Portal',
                message=(
                    'This is a test email from Radhika Apartment Maintenance Portal.\n\n'
                    'If you received this, Gmail SMTP is configured correctly!\n\n'
                    f'Sent at: {datetime.datetime.now().strftime("%d %B %Y %I:%M %p")}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            return Response({
                'success': True,
                'message': f'✅ Test email sent to {to_email} — check your inbox (and spam folder)',
                'config':  config_info,
            })
        except Exception as e:
            logger.error(f"Test email failed: {e}")
            return Response({
                'success': False,
                'error':   str(e),
                'config':  config_info,
                'fix': (
                    'Common fixes:\n'
                    '1. Make sure EMAIL_HOST_USER is your Gmail address\n'
                    '2. EMAIL_HOST_PASSWORD must be a 16-char App Password (NOT your normal Gmail password)\n'
                    '3. Enable 2-Step Verification first at https://myaccount.google.com/security\n'
                    '4. Then create App Password at https://myaccount.google.com/apppasswords'
                )
            }, status=status.HTTP_502_BAD_GATEWAY)


# ── SEND REMINDER TO ALL OVERDUE ──────────────────────────────────────
=======
        body += f"\nYou can also check your balance anytime at: {portal_url}\n"
    body += "\nThank you,\nRadhika Apartment"
    return body


# ── ADMIN: Send reminder to ALL overdue/pending flats ──────────────────
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d
class SendOverdueRemindersView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
<<<<<<< HEAD
        status_filter = request.data.get('status', 'overdue')
        wing_filter   = request.data.get('wing')

        # Validate email config first
        if not getattr(settings, 'EMAIL_HOST_USER', ''):
            return Response({
                'error': 'EMAIL_HOST_USER not set. Add it to Render environment variables.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if not getattr(settings, 'EMAIL_HOST_PASSWORD', ''):
            return Response({
                'error': 'EMAIL_HOST_PASSWORD not set. Add Gmail App Password to Render environment variables.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        flats = list(
            Flat.objects.select_related('wing','floor','owner')
            .prefetch_related('payments','maintenance_dues')
            .order_by('wing__name','floor__number','room_number')
        )

        if wing_filter:
            flats = [f for f in flats if f.wing.name == wing_filter.upper()]
=======
        # Optional filters: status=overdue|pending|all (default overdue), wing=A|B
        status_filter = request.data.get('status', 'overdue')
        wing_filter    = request.data.get('wing')

        flats = (Flat.objects.select_related('wing','floor','owner')
                 .prefetch_related('payments','maintenance_dues')
                 .order_by('wing__name','floor__number','room_number'))

        if wing_filter:
            flats = [f for f in flats if f.wing.name == wing_filter.upper()]
        else:
            flats = list(flats)
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d

        if status_filter != 'all':
            flats = [f for f in flats if f.payment_status == status_filter]

        sent, skipped, failed = [], [], []

        for flat in flats:
            owner = getattr(flat, 'owner', None)
<<<<<<< HEAD

            if not owner:
                skipped.append({'flat': flat.flat_number, 'reason': 'No owner record'})
                continue
            if not owner.email or owner.email.strip() == '':
                skipped.append({'flat': flat.flat_number, 'reason': 'No email address'})
                continue
            if flat.total_balance <= 0:
                skipped.append({'flat': flat.flat_number, 'reason': 'No balance due'})
=======
            if not owner or not owner.email:
                skipped.append(flat.flat_number)
                continue
            if flat.total_balance <= 0:
                skipped.append(flat.flat_number)
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d
                continue

            try:
                pdf_bytes = build_receipt_pdf_bytes(flat)
                email = EmailMessage(
<<<<<<< HEAD
                    subject=f"Maintenance Due Reminder — Flat {flat.flat_number} | Radhika Apartment",
                    body=reminder_email_body(flat, owner),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[owner.email.strip()],
                )
                email.attach(
                    f"receipt_{flat.flat_number}_{datetime.date.today()}.pdf",
                    pdf_bytes,
                    "application/pdf"
                )
                email.send(fail_silently=False)
                sent.append(flat.flat_number)
                logger.info(f"Reminder sent for {flat.flat_number} to {owner.email}")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Failed to send reminder for {flat.flat_number}: {error_msg}")
                failed.append({'flat': flat.flat_number, 'error': error_msg})
=======
                    subject=f"Maintenance Due Reminder - Flat {flat.flat_number} | Radhika Apartment",
                    body=reminder_email_body(flat, owner),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[owner.email],
                )
                email.attach(f"receipt_{flat.flat_number}.pdf", pdf_bytes, "application/pdf")
                email.send(fail_silently=False)
                sent.append(flat.flat_number)
            except Exception as e:
                failed.append({'flat': flat.flat_number, 'error': str(e)})
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d

        return Response({
            'sent_count':    len(sent),
            'skipped_count': len(skipped),
            'failed_count':  len(failed),
            'sent':    sent,
            'skipped': skipped,
            'failed':  failed,
        })


<<<<<<< HEAD
# ── SEND REMINDER TO SINGLE FLAT ─────────────────────────────────────
=======
# ── ADMIN: Send reminder to a SINGLE flat ───────────────────────────────
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d
class SendSingleReminderView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, flat_number):
<<<<<<< HEAD
        # Validate email config first
        if not getattr(settings, 'EMAIL_HOST_USER', ''):
            return Response(
                {'error': 'EMAIL_HOST_USER not configured on server. Check Render environment variables.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        if not getattr(settings, 'EMAIL_HOST_PASSWORD', ''):
            return Response(
                {'error': 'EMAIL_HOST_PASSWORD not configured. Add Gmail App Password to Render environment variables.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            flat = Flat.objects.select_related('wing','floor','owner').get(flat_number=flat_number)
        except Flat.DoesNotExist:
            return Response({'error': f'Flat {flat_number} not found.'}, status=status.HTTP_404_NOT_FOUND)

        owner = getattr(flat, 'owner', None)
        if not owner:
            return Response({'error': 'No owner record for this flat.'}, status=status.HTTP_400_BAD_REQUEST)
        if not owner.email or owner.email.strip() == '':
            return Response({'error': 'No email address on file for this flat owner. Please update the owner email first in Admin panel.'}, status=status.HTTP_400_BAD_REQUEST)
=======
        try:
            flat = Flat.objects.select_related('wing','floor','owner').get(flat_number=flat_number)
        except Flat.DoesNotExist:
            return Response({'error':'Flat not found'}, status=status.HTTP_404_NOT_FOUND)

        owner = getattr(flat, 'owner', None)
        if not owner or not owner.email:
            return Response({'error':'No email address on file for this flat.'},
                             status=status.HTTP_400_BAD_REQUEST)
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d

        try:
            pdf_bytes = build_receipt_pdf_bytes(flat)
            email = EmailMessage(
<<<<<<< HEAD
                subject=f"Maintenance Receipt — Flat {flat.flat_number} | Radhika Apartment",
                body=reminder_email_body(flat, owner),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[owner.email.strip()],
            )
            email.attach(
                f"receipt_{flat.flat_number}_{datetime.date.today()}.pdf",
                pdf_bytes,
                "application/pdf"
            )
            email.send(fail_silently=False)
            logger.info(f"Single reminder sent for {flat.flat_number} to {owner.email}")
        except Exception as e:
            logger.error(f"Single reminder failed for {flat.flat_number}: {e}")
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({
            'success': True,
            'message': f'Email sent successfully to {owner.email}',
            'flat': flat.flat_number,
            'owner': owner.name,
        })
=======
                subject=f"Maintenance Receipt - Flat {flat.flat_number} | Radhika Apartment",
                body=reminder_email_body(flat, owner),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[owner.email],
            )
            email.attach(f"receipt_{flat.flat_number}.pdf", pdf_bytes, "application/pdf")
            email.send(fail_silently=False)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({'message': f'Email sent to {owner.email}'})
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d
