"""Service voor PDF-export van resultaten."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def build_result_pdf(
    sales_price: float,
    total_co2: float,
    bom_rows: list[dict],
    material_rows: list[dict],
) -> bytes:
    """Genereer een eenvoudige PDF met resultaten."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    _, height = A4

    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "Prefab LBK set - Resultaatrapport")

    y -= 30
    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, y, f"Verkoopprijs: € {sales_price:.2f}")
    y -= 18
    pdf.drawString(40, y, f"Totale CO2-uitstoot: {total_co2:.2f} kg CO2e")

    y -= 30
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(40, y, "Stuklijst")

    y -= 20
    pdf.setFont("Helvetica", 10)
    for row in bom_rows:
        line = f"{row['Artikel']} | {row['Artikelnummer']} | {row['Omschrijving']} | aantal/lengte: {row['Aantal']}"
        pdf.drawString(40, y, line[:110])
        y -= 14
        if y < 80:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

    y -= 10
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(40, y, "Materialenpaspoort")

    y -= 20
    pdf.setFont("Helvetica", 10)
    for row in material_rows:
        pdf.drawString(40, y, f"{row['Materiaal']}: {row['Totaal (kg)']:.3f} kg")
        y -= 14
        if y < 80:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

    pdf.save()
    return buffer.getvalue()