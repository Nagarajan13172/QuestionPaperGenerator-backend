"""
Syllabus Parser Service
Extracts text from files and parses units/topics
"""
import re
import logging
from typing import List
import fitz  # PyMuPDF

from app.models import Unit

logger = logging.getLogger(__name__)


class SyllabusParser:
    """Parse syllabus content and extract unit            # If no units found with patterns, try inline extraction first
            if not units:
                logger.warning("No units found with line patterns, trying inline extraction")
                units = self._extract_units_from_inline_text(content)
            
            # If still no units, try smart parse
            if not units:
                logger.warning("Inline extraction failed, attempting smart split")
                units = self._smart_parse_without_units(content)pics"""
    
    def __init__(self):
        self.unit_patterns = [
            r'(?i)^unit\s+(\d+)\s*:\s*(.+)',  # Match "Unit 1: LISTS"
            r'(?i)^unit\s+(\d+)\s+(.+)',  # Match "Unit 1 LISTS"
            r'(?i)^chapter\s+(\d+)\s*[:\-–—]?\s*(.+)',
            r'(?i)^module\s+(\d+)\s*[:\-–—]?\s*(.+)',
            r'(?i)^(\d+)\.\s*(.+)',  # Numbered sections like "1. Introduction"
            r'(?i)^unit\s+([IVX]+)\s*[:\-–—]?\s*(.+)',  # Roman numerals
        ]
        # Pattern to find UNIT within text (not just at line start)
        self.inline_unit_pattern = r'UNIT\s+([IVX]+)\s+([A-Z\s&,]+?)\s+\d+'
        
        # Patterns to identify and skip reference/textbook sections
        self.skip_patterns = [
            r'(?i)(text\s*book|reference|bibliography|suggested\s+reading)',
            r'(?i)(edition|publisher|publication|pearson|mcgraw|wiley)',
            r'(?i)(downloaded\s+from|enggtree\.com|copyright)',
        ]
    
    def _should_skip_line(self, line: str) -> bool:
        """Check if a line should be skipped (references, etc.)"""
        for pattern in self.skip_patterns:
            if re.search(pattern, line):
                return True
        return False
    
    def _extract_units_from_inline_text(self, content: str) -> List[Unit]:
        """
        Extract units when they appear inline like "UNIT I LISTS 9 ..."
        This handles PDFs where all content is in one paragraph
        """
        units = []
        
        # Find all UNIT markers
        matches = list(re.finditer(self.inline_unit_pattern, content))
        
        if len(matches) < 2:
            return []
        
        logger.info(f"Found {len(matches)} inline unit markers")
        
        for i, match in enumerate(matches):
            unit_number_raw = match.group(1)
            unit_title = match.group(2).strip()
            
            # Convert Roman to number
            roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 
                        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
            unit_number = roman_map.get(unit_number_raw, i + 1)
            
            # Extract content for this unit (from this match to next match or end)
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            unit_content = content[start_pos:end_pos].strip()
            
            # Extract topics from unit content
            # Topics are usually separated by – or listed after certain keywords
            topics = []
            
            # Split by common delimiters
            parts = re.split(r'\s*[–—]\s*', unit_content)
            for part in parts:
                part = part.strip()
                # Skip very short or reference-like parts
                if len(part) > 10 and not self._should_skip_line(part):
                    # Clean up
                    part = re.sub(r'\s+', ' ', part)
                    part = re.sub(r'^\d+\s*', '', part)  # Remove leading numbers
                    if part:
                        topics.append(part[:200])  # Limit topic length
            
            # Remove duplicates while preserving order
            seen = set()
            unique_topics = []
            for topic in topics:
                if topic.lower() not in seen:
                    seen.add(topic.lower())
                    unique_topics.append(topic)
            
            if unique_topics:
                unit = Unit(
                    id=f"unit_{unit_number}",
                    title=unit_title,
                    topics=unique_topics[:15],  # Limit to 15 topics
                    order=unit_number
                )
                units.append(unit)
                logger.info(f"Extracted inline unit: {unit_title} with {len(unique_topics)} topics")
        
        return units
    
    def _preprocess_pdf_text(self, text: str) -> str:
        """
        Preprocess PDF text to handle common issues
        - Remove page breaks and extra whitespace
        - Fix line breaks in middle of sentences
        - Remove common PDF artifacts
        """
        # Remove common PDF artifacts
        text = re.sub(r'Downloaded from \w+\.com', '', text, flags=re.IGNORECASE)
        text = re.sub(r'EnggTree\.com', '', text, flags=re.IGNORECASE)
        
        # Remove page numbers (standalone numbers on lines)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Fix broken lines (line breaks in middle of sentences)
        # Join lines that don't end with period, colon, or dash
        lines = text.split('\n')
        fixed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                fixed_lines.append('')
                i += 1
                continue
            
            # If line doesn't end with punctuation and next line doesn't start a new section
            while (i + 1 < len(lines) and 
                   not line.endswith(('.', ':', '–', '-', '—')) and
                   not re.match(r'(?i)^(unit|chapter|module|\d+\.)', lines[i + 1].strip())):
                next_line = lines[i + 1].strip()
                if next_line:
                    line += ' ' + next_line
                i += 1
            
            fixed_lines.append(line)
            i += 1
        
        text = '\n'.join(fixed_lines)
        
        # Normalize whitespace
        text = re.sub(r' +', ' ', text)
        
        return text
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file with cleaning
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    page_text = page.get_text()
                    # Clean up the text
                    page_text = page_text.replace('\x00', '')  # Remove null bytes
                    text += page_text + "\n"
            
            # Additional cleaning
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.replace(' - ', ' – ')  # Normalize dashes
            
            logger.info(f"Extracted {len(text)} characters from PDF")
            logger.debug(f"First 500 chars: {text[:500]}")
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def parse_text(self, content: str) -> List[Unit]:
        """
        Parse syllabus text and extract units with topics
        
        Args:
            content: Raw syllabus text
            
        Returns:
            List of parsed units
        """
        units = []
        
        try:
            logger.info(f"Parsing syllabus content ({len(content)} characters)")
            
            # Preprocess PDF text to fix common issues
            content = self._preprocess_pdf_text(content)
            logger.debug(f"After preprocessing: {len(content)} characters")
            
            # Split content into lines
            lines = content.split('\n')
            
            current_unit = None
            current_topics = []
            unit_count = 0
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or len(line) < 3:
                    continue
                
                # Skip reference/textbook sections
                if self._should_skip_line(line):
                    logger.debug(f"Skipping reference line: {line[:60]}")
                    continue
                
                # Check if line matches any unit pattern
                unit_matched = False
                for pattern in self.unit_patterns:
                    match = re.match(pattern, line)
                    if match:
                        unit_number_raw = match.group(1)
                        unit_title = match.group(2).strip()
                        
                        # Skip if title looks like a reference
                        if self._should_skip_line(unit_title):
                            logger.debug(f"Skipping reference unit: {unit_title[:60]}")
                            continue
                        
                        # Convert Roman numerals to numbers
                        if unit_number_raw.upper() in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']:
                            roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 
                                       'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
                            unit_number = roman_map.get(unit_number_raw.upper(), unit_count + 1)
                        else:
                            unit_number = unit_number_raw
                        
                        # Save previous unit if exists
                        if current_unit and current_topics:
                            current_unit.topics = current_topics
                            units.append(current_unit)
                            logger.debug(f"Saved unit: {current_unit.title} with {len(current_topics)} topics")
                        
                        # Create new unit
                        unit_count += 1
                        
                        # Remove trailing dots, colons, etc.
                        unit_title = re.sub(r'[:\.\-–—]+$', '', unit_title).strip()
                        
                        # Skip if title is too short (likely parsing error)
                        if len(unit_title) < 3:
                            continue
                        
                        current_unit = Unit(
                            id=f"unit_{unit_count}",
                            title=unit_title,
                            topics=[],
                            order=unit_count
                        )
                        current_topics = []
                        unit_matched = True
                        logger.info(f"Found unit {unit_count}: {unit_title} (line {line_num})")
                        break
                
                # If not a unit header, treat as a topic
                if not unit_matched and current_unit:
                    # Remove bullet points and numbering
                    topic = re.sub(r'^[\-\*\•\d\.]+\s*', '', line)
                    topic = topic.strip()
                    
                    # Skip reference lines in topics
                    if self._should_skip_line(topic):
                        continue
                    
                    # Filter out very short lines and common headers
                    if (topic and len(topic) > 5 and 
                        not re.match(r'(?i)^(topics?|syllabus|course|objectives?|unit\s+[IVX]+):?$', topic)):
                        current_topics.append(topic)
                        logger.debug(f"  Added topic: {topic[:50]}...")
            
            # Add the last unit
            if current_unit:
                current_unit.topics = current_topics
                units.append(current_unit)
                logger.debug(f"Saved final unit: {current_unit.title} with {len(current_topics)} topics")
            
            # If no units found with patterns, try inline extraction first
            if not units:
                logger.warning("No units found with line patterns, trying inline extraction")
                units = self._extract_units_from_inline_text(content)
            
            # If still no units, try smart parse
            if not units:
                logger.warning("Inline extraction failed, attempting smart split")
                units = self._smart_parse_without_units(content)
            
            # Ensure all units have at least some topics and filter out likely references
            units = [u for u in units if u.topics and not self._should_skip_line(u.title)]
            
            # If we ended up with no units or very few, try inline then smart parse
            if len(units) < 2:
                logger.warning(f"Only {len(units)} valid units found, trying inline extraction")
                inline_units = self._extract_units_from_inline_text(content)
                if len(inline_units) > len(units):
                    units = inline_units
                elif not units:
                    logger.warning("Inline failed, attempting full reparse")
                    units = self._smart_parse_without_units(content)
            
            logger.info(f"✓ Successfully parsed {len(units)} units from syllabus")
            for unit in units:
                logger.info(f"  - {unit.title}: {len(unit.topics)} topics")
            
            return units
            
        except Exception as e:
            logger.error(f"Error parsing syllabus text: {e}", exc_info=True)
            raise
    
    def _smart_parse_without_units(self, content: str) -> List[Unit]:
        """
        Fallback parser when no unit headers are found.
        Splits content into logical sections based on blank lines.
        """
        sections = re.split(r'\n\s*\n', content)  # Split by blank lines
        units = []
        
        for i, section in enumerate(sections, 1):
            section = section.strip()
            if not section or len(section) < 10:
                continue
            
            lines = [l.strip() for l in section.split('\n') if l.strip()]
            if not lines:
                continue
            
            # First line might be a title
            title = lines[0] if len(lines[0]) < 100 else f"Section {i}"
            topics = [re.sub(r'^[\-\*\•\d\.]+\s*', '', l).strip() 
                     for l in lines[1:] if len(l.strip()) > 3]
            
            if not topics and len(lines) > 1:
                # If first line is too long, treat all as topics
                title = f"Section {i}"
                topics = [re.sub(r'^[\-\*\•\d\.]+\s*', '', l).strip() 
                         for l in lines if len(l.strip()) > 3]
            
            if topics:
                units.append(Unit(
                    id=f"unit_{i}",
                    title=title[:100],  # Limit title length
                    topics=topics[:20],  # Limit topics per unit
                    order=i
                ))
        
        if not units:
            # Last resort: create one unit with all non-empty lines
            all_lines = [l.strip() for l in content.split('\n') 
                        if l.strip() and len(l.strip()) > 3]
            if all_lines:
                units.append(Unit(
                    id="unit_1",
                    title=all_lines[0][:100] if all_lines[0] else "Course Content",
                    topics=all_lines[1:21] if len(all_lines) > 1 else all_lines[:20],
                    order=1
                ))
        
        logger.info(f"Smart parse created {len(units)} sections")
        return units
    
    def validate_units(self, units: List[Unit]) -> bool:
        """
        Validate parsed units
        
        Args:
            units: List of units to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not units:
            return False
        
        for unit in units:
            if not unit.title or not unit.id:
                return False
            if not unit.topics or len(unit.topics) == 0:
                return False
        
        return True
