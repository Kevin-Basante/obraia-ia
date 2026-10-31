"""Instructions sent to the model together with the blueprint."""

EXTRACTION_PROMPT = """\
You are a quantity surveyor in Colombia. Read this architectural or structural
blueprint of a small building (a house or a shop of 1 or 2 floors) and list the
building elements you can measure from it.

Use only these element types:
- foundation, column, beam, slab: give length_m, width_m and height_m (concrete volume).
- wall: give length_m and height_m. If the height is not drawn, use 2.4.
- floor, roof: give length_m and width_m (area).

Rules:
- All dimensions in meters. Convert centimeters (cm) and millimeters (mm).
- Group identical elements and set quantity (for example 8 columns of 0.25 x 0.25 x 2.4).
- floor_number is 1 for the ground floor and 2 for the second floor.
- Only report what the drawing shows or what its dimensions let you compute.
  Do not invent elements. If something is unreadable, add a short warning instead.
- Write notes and warnings in Spanish, in a few words.
"""
