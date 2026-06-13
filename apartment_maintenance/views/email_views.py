import io
import datetime

from django.core.mail import EmailMessage
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)

from apartment_maintenance.models import Flat


def build_receipt_pdf_bytes(flat):
    """Generate the same receipt PDF as FlatReceiptPDFView, return raw bytes."""
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
    header_tbl.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BOTTOMPADDING',(0,0),(-1,-1),12),
    ]))
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
        Paragraph(f'<b><font size=11>Outstanding Balance</font></b><br/><br/>'
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
                str(i),
                pay.payment_date.strftime('%d/%m/%Y'),
                f'{pay.amount:,.0f}',
                pay.payment_mode.upper(),
                pay.transaction_id or '—',
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
        '<font size=8 color="grey">This is a computer-generated receipt. '
        'For queries contact the society office.</font>',
        ParagraphStyle('Footer', alignment=1, parent=styles['Normal'])))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def reminder_email_body(flat, owner):
    months = int(flat.total_balance / flat.monthly_maintenance) if flat.total_balance > 0 else 0
    portal_url = getattr(settings, 'FRONTEND_URL', '')
    body = f"""Dear {owner.name},

This is a friendly reminder regarding your maintenance dues for Flat {flat.flat_number}, Radhika Apartment.

Outstanding Balance: Rs. {flat.total_balance:,.0f}
Pending Months: {months}
Monthly Charge: Rs. {flat.monthly_maintenance:,.0f}

Please clear the dues at the earliest. A detailed receipt is attached to this email for your reference.
"""
    if portal_url:
        body += f"\nYou can also check your balance anytime at: {portal_url}\n"
    body += "\nThank you,\nRadhika Apartment"
    return body


# ── ADMIN: Send reminder to ALL overdue/pending flats ──────────────────
class SendOverdueRemindersView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
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

        if status_filter != 'all':
            flats = [f for f in flats if f.payment_status == status_filter]

        sent, skipped, failed = [], [], []

        for flat in flats:
            owner = getattr(flat, 'owner', None)
            if not owner or not owner.email:
                skipped.append(flat.flat_number)
                continue
            if flat.total_balance <= 0:
                skipped.append(flat.flat_number)
                continue

            try:
                pdf_bytes = build_receipt_pdf_bytes(flat)
                email = EmailMessage(
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

        return Response({
            'sent_count':    len(sent),
            'skipped_count': len(skipped),
            'failed_count':  len(failed),
            'sent':    sent,
            'skipped': skipped,
            'failed':  failed,
        })


# ── ADMIN: Send reminder to a SINGLE flat ───────────────────────────────
class SendSingleReminderView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, flat_number):
        try:
            flat = Flat.objects.select_related('wing','floor','owner').get(flat_number=flat_number)
        except Flat.DoesNotExist:
            return Response({'error':'Flat not found'}, status=status.HTTP_404_NOT_FOUND)

        owner = getattr(flat, 'owner', None)
        if not owner or not owner.email:
            return Response({'error':'No email address on file for this flat.'},
                             status=status.HTTP_400_BAD_REQUEST)

        try:
            pdf_bytes = build_receipt_pdf_bytes(flat)
            email = EmailMessage(
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
