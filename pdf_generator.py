# pdf_generator.py

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

def create_beautiful_pdf(data):
    """
    DIAGNOSTIC VERSION: This function will not produce a PDF if an error occurs.
    Instead, it will try to build the document element by element and report
    exactly which element is causing the 'TypeError'.
    """
    buffer = BytesIO()
    margin_in_points = 0.7 * 72 # 50.4

    doc = SimpleDocTemplate(buffer,
                            pagesize=A4,
                            rightMargin=margin_in_points,
                            leftMargin=margin_in_points,
                            topMargin=margin_in_points,
                            bottomMargin=margin_in_points)
    story = []

    # --- Define Styles from Scratch ---
    styles = StyleSheet1()
    styles.add(ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=10.5, leading=14, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='NameStyle', fontName='Helvetica-Bold', fontSize=24, alignment=TA_CENTER, spaceAfter=16))
    styles.add(ParagraphStyle(name='ContactStyle', fontName='Helvetica', fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#555555'), spaceAfter=6))
    styles.add(ParagraphStyle(name='SectionTitleStyle', fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor('#2C3E50'), spaceAfter=2, leading=16))
    styles.add(ParagraphStyle(name='EntryTitleStyle', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#34495E'), spaceAfter=1, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='EntrySubtitleStyle', fontName='Helvetica-Oblique', fontSize=10, textColor=colors.HexColor('#7F8C8D'), spaceAfter=5, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='BodyStyle', fontName='Helvetica', fontSize=10.5, alignment=TA_JUSTIFY, leading=14, spaceAfter=12))
    styles.add(ParagraphStyle(name='PillStyle', fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.HexColor('#34495E'), backColor=colors.HexColor('#EAECEE'), borderPadding=4, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='ListItem', parent=styles['BodyStyle'], leftIndent=14, spaceAfter=4))

    styles.add(ParagraphStyle(name='PillTextStyle',
                              fontName='Helvetica-Bold',
                              fontSize=8,
                              textColor=colors.HexColor('#31333F'),
                              alignment=TA_CENTER,
                              leading=12))

    def sanitize(text):
        if not isinstance(text, str): return ""
        return text.replace('&', '&').replace('<', '<').replace('>', '>')

    # --- Build the Story (The list of PDF elements) ---
    # This part of the code remains the same
    personal_info = data.get('personal_info', {})
    story.append(Paragraph(sanitize(personal_info.get('name', '')), styles['NameStyle']))
    contact_text = f"{sanitize(personal_info.get('email', ''))} | {sanitize(personal_info.get('phone', ''))} | <a href='{sanitize(personal_info.get('linkedin', ''))}' color='blue'><u>LinkedIn Profile</u></a>"
    story.append(Paragraph(contact_text, styles['ContactStyle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#BDC3C7'), spaceAfter=14))

    if data.get('summary'):
        story.append(Paragraph("PROFESSIONAL SUMMARY", styles['SectionTitleStyle']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#BDC3C7'), spaceAfter=8))
        story.append(Paragraph(sanitize(data.get('summary', '')), styles['BodyStyle']))
    
    if data.get('experience'):
        story.append(Paragraph("WORK EXPERIENCE", styles['SectionTitleStyle']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#BDC3C7'), spaceAfter=8))
        for job in data.get('experience', []):
            if job.get('title'):
                # --- FIX APPLIED HERE ---
                story.append(Paragraph(sanitize(job.get('title', '')), styles['EntryTitleStyle']))
                story.append(Paragraph(f"{sanitize(job.get('company', ''))} | {sanitize(job.get('dates', ''))}", styles['EntrySubtitleStyle']))
                story.append(Paragraph(sanitize(job.get('description', '')).replace('\n', '<br/>'), styles['BodyStyle']))
                if not (job == data['experience'][-1]): story.append(Spacer(1, 12))
    

    # (The rest of the story building is the same...)

    if data.get('projects'):
        story.append(Paragraph("PROJECTS", styles['SectionTitleStyle']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#BDC3C7'), spaceAfter=8))
        for proj in data.get('projects', []):
            if proj.get('title'):
                story.append(Paragraph(sanitize(proj.get('title', '')), styles['EntryTitleStyle']))
                story.append(Paragraph(sanitize(proj.get('dates', '')), styles['EntrySubtitleStyle']))
                story.append(Paragraph(sanitize(proj.get('description', '')).replace('\n', '<br/>'), styles['BodyStyle']))
                if not (proj == data['projects'][-1]): story.append(Spacer(1, 12))

    if data.get('achievements'):
        story.append(Spacer(1, 12))
        story.append(Paragraph("ACHIEVEMENTS", styles['SectionTitleStyle']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#BDC3C7'), spaceAfter=8))
        for ach in data.get('achievements', []):
            if ach.get('description'):
                story.append(Paragraph(f"• {sanitize(ach.get('description', ''))}", styles['ListItem']))

    
    if data.get('education'):
        story.append(Paragraph("EDUCATION", styles['SectionTitleStyle']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#BDC3C7'), spaceAfter=8))
        for edu in data.get('education', []):
            if edu.get('degree'):
                story.append(Paragraph(sanitize(edu.get('degree', '')), styles['EntryTitleStyle']))
                story.append(Paragraph(sanitize(edu.get('institution_dates', '')), styles['EntrySubtitleStyle']))
    
    if data.get('skills'):
        story.append(Spacer(1, 12))
        story.append(Paragraph("SKILLS", styles['SectionTitleStyle']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#BDC3C7'), spaceAfter=8))

        skills_list = data.get('skills', [])
        skill_paragraphs = [Paragraph(sanitize(skill), styles['PillTextStyle']) for skill in skills_list]

        num_columns = 4
        table_data = []
        for i in range(0, len(skill_paragraphs), num_columns):
            row = skill_paragraphs[i:i + num_columns]
            # Pad the last row with empty strings to keep the grid structure
            while len(row) < num_columns:
                row.append("")
            table_data.append(row)

        # --- THIS IS THE KEY FIX ---
        # Calculate the available width for the table (Page width - left margin - right margin)
        available_width = doc.width - 2
        # Divide the available width equally among the columns
        column_width = available_width / num_columns
        skill_table = Table(table_data, colWidths=[column_width] * num_columns, hAlign='LEFT')

        table_style_commands = []
        for row_idx, row in enumerate(table_data):
            for col_idx, cell_content in enumerate(row):
                # Only apply styling to cells that actually contain a skill
                if cell_content != "":
                    # Add a light grey background to the cell
                    table_style_commands.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.HexColor('#f0f2f6')))
                    # Add inner padding to the cell
                    table_style_commands.append(('LEFTPADDING', (col_idx, row_idx), (col_idx, row_idx), 8))
                    table_style_commands.append(('RIGHTPADDING', (col_idx, row_idx), (col_idx, row_idx), 8))
                    table_style_commands.append(('TOPPADDING', (col_idx, row_idx), (col_idx, row_idx), 6))
                    table_style_commands.append(('BOTTOMPADDING', (col_idx, row_idx), (col_idx, row_idx), 6))

        # Add grid lines to create space, and a border for the cells
        table_style_commands.append(('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey))
        table_style_commands.append(('VALIGN', (0,0), (-1,-1), 'MIDDLE'))
        
        skill_table.setStyle(TableStyle(table_style_commands))
        story.append(skill_table)


    # --- THE DIAGNOSTIC LOOP ---
    # We will now try to build a tiny PDF for each element one by one.
    # The one that fails is our culprit.
    for i, flowable in enumerate(story):
        try:
            # Create a temporary document with just this one element
            temp_buffer = BytesIO()
            temp_doc = SimpleDocTemplate(temp_buffer)
            temp_doc.build([flowable])
        except TypeError as e:
            # If we get the specific TypeError, we've found the bug!
            if "unsupported operand type(s) for -: 'str' and 'float'" in str(e):
                # Now we create a detailed error report.
                error_content = "N/A"
                style_name = "N/A (Not a Paragraph)"
                if isinstance(flowable, Paragraph):
                    error_content = flowable.text
                    style_name = flowable.style.name

                debug_message = f"""
                ====================================================================
                DIAGNOSTIC REPORT: TypeError FOUND!
                ====================================================================

                The error is caused by the following element in the PDF story.
                ReportLab failed during a calculation while trying to render this specific piece of content.

                - Element Index: {i}
                - Element Type: {type(flowable).__name__}
                - Style Name: {style_name}
                
                --- FAILING CONTENT ---
                {error_content}
                -----------------------

                Please examine this content and the style being applied to it.
                The issue is likely a corrupted value being passed to a style property.
                """
                raise RuntimeError(debug_message) from e
            else:
                # If it's a different error, we still want to know.
                raise e
    
    # If the loop completes without error, build the final document.
    # This part will likely not be reached if the error is happening.
    doc.build(story)
    
    pdf_value = buffer.getvalue()
    buffer.close()
    return pdf_value