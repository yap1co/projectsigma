-- Career Interests and Keywords Management
-- This migration creates tables to store career interests, keywords, and conflicts
-- This replaces hardcoded values in the recommendation engine

-- Career Interest Categories
CREATE TABLE IF NOT EXISTS career_interest (
    interest_id VARCHAR(50) PRIMARY KEY,
    interest_name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Keywords for matching courses to career interests
CREATE TABLE IF NOT EXISTS career_interest_keyword (
    keyword_id VARCHAR(50) PRIMARY KEY,
    interest_id VARCHAR(50) NOT NULL REFERENCES career_interest(interest_id) ON DELETE CASCADE,
    keyword VARCHAR(100) NOT NULL,
    match_type VARCHAR(20) DEFAULT 'contains' CHECK (match_type IN ('contains', 'exact', 'starts_with', 'ends_with')),
    priority INTEGER DEFAULT 0, -- Higher priority keywords are checked first
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(interest_id, keyword)
);

-- Conflicting career interests (e.g., Business & Finance conflicts with Sciences)
CREATE TABLE IF NOT EXISTS career_interest_conflict (
    conflict_id VARCHAR(50) PRIMARY KEY,
    interest_id VARCHAR(50) NOT NULL REFERENCES career_interest(interest_id) ON DELETE CASCADE,
    conflicting_interest_id VARCHAR(50) NOT NULL REFERENCES career_interest(interest_id) ON DELETE CASCADE,
    conflict_strength VARCHAR(20) DEFAULT 'strong' CHECK (conflict_strength IN ('weak', 'medium', 'strong')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(interest_id, conflicting_interest_id),
    CHECK (interest_id != conflicting_interest_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_career_interest_keyword_interest ON career_interest_keyword(interest_id);
CREATE INDEX IF NOT EXISTS idx_career_interest_keyword_keyword ON career_interest_keyword(keyword);
CREATE INDEX IF NOT EXISTS idx_career_interest_keyword_active ON career_interest_keyword(interest_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_career_interest_conflict_interest ON career_interest_conflict(interest_id);
CREATE INDEX IF NOT EXISTS idx_career_interest_conflict_conflicting ON career_interest_conflict(conflicting_interest_id);
CREATE INDEX IF NOT EXISTS idx_career_interest_active ON career_interest(is_active) WHERE is_active = TRUE;

-- Insert default career interests
INSERT INTO career_interest (interest_id, interest_name, display_name, description, display_order) VALUES
    ('CI001', 'Business & Finance', 'Business & Finance', 'Business, finance, accounting, economics, management, banking, investment, marketing', 1),
    ('CI002', 'Medicine & Healthcare', 'Medicine & Healthcare', 'Medicine, health, nursing, pharmacy, dentistry, veterinary, biomedical', 2),
    ('CI003', 'Engineering & Technology', 'Engineering & Technology', 'Engineering, technology, computer science, software, electrical, mechanical, civil', 3),
    ('CI004', 'Law', 'Law', 'Law, legal studies, jurisprudence, criminology', 4),
    ('CI005', 'Education', 'Education', 'Education, teaching, pedagogy', 5),
    ('CI006', 'Arts & Humanities', 'Arts & Humanities', 'Arts, humanities, history, literature, philosophy, classics', 6),
    ('CI007', 'Sciences', 'Sciences', 'Science, physics, chemistry, biology, mathematics', 7),
    ('CI008', 'Social Sciences', 'Social Sciences', 'Sociology, psychology, politics, international relations, anthropology', 8),
    ('CI009', 'Creative Arts', 'Creative Arts', 'Art, design, creative, fine art, graphic design, fashion', 9),
    ('CI010', 'Sports & Fitness', 'Sports & Fitness', 'Sports, fitness, exercise, physical education, kinesiology', 10)
ON CONFLICT (interest_name) DO NOTHING;

-- Insert keywords for Business & Finance
INSERT INTO career_interest_keyword (keyword_id, interest_id, keyword, priority) VALUES
    ('KW001', 'CI001', 'business', 10),
    ('KW002', 'CI001', 'finance', 10),
    ('KW003', 'CI001', 'accounting', 9),
    ('KW004', 'CI001', 'economics', 9),
    ('KW005', 'CI001', 'management', 8),
    ('KW006', 'CI001', 'banking', 8),
    ('KW007', 'CI001', 'investment', 8),
    ('KW008', 'CI001', 'marketing', 7),
    ('KW009', 'CI001', 'entrepreneurship', 7),
    ('KW010', 'CI001', 'commerce', 7),
    ('KW011', 'CI001', 'financial', 8)
ON CONFLICT (interest_id, keyword) DO NOTHING;

-- Insert keywords for Medicine & Healthcare
INSERT INTO career_interest_keyword (keyword_id, interest_id, keyword, priority) VALUES
    ('KW012', 'CI002', 'medicine', 10),
    ('KW013', 'CI002', 'health', 9),
    ('KW014', 'CI002', 'nursing', 9),
    ('KW015', 'CI002', 'pharmacy', 8),
    ('KW016', 'CI002', 'dentistry', 8),
    ('KW017', 'CI002', 'veterinary', 7),
    ('KW018', 'CI002', 'biomedical', 7),
    ('KW019', 'CI002', 'medical', 8)
ON CONFLICT (interest_id, keyword) DO NOTHING;

-- Insert keywords for Engineering & Technology
INSERT INTO career_interest_keyword (keyword_id, interest_id, keyword, priority) VALUES
    ('KW020', 'CI003', 'engineering', 10),
    ('KW021', 'CI003', 'technology', 9),
    ('KW022', 'CI003', 'computer', 9),
    ('KW023', 'CI003', 'software', 8),
    ('KW024', 'CI003', 'electrical', 8),
    ('KW025', 'CI003', 'mechanical', 8),
    ('KW026', 'CI003', 'civil', 7),
    ('KW027', 'CI003', 'computing', 9),
    ('KW028', 'CI003', 'tech', 6),
    ('KW029', 'CI003', 'physics', 5)
ON CONFLICT (interest_id, keyword) DO NOTHING;

-- Insert keywords for Law
INSERT INTO career_interest_keyword (keyword_id, interest_id, keyword, priority) VALUES
    ('KW030', 'CI004', 'law', 10),
    ('KW031', 'CI004', 'legal', 9),
    ('KW032', 'CI004', 'jurisprudence', 8),
    ('KW033', 'CI004', 'criminology', 8)
ON CONFLICT (interest_id, keyword) DO NOTHING;

-- Insert keywords for Education
INSERT INTO career_interest_keyword (keyword_id, interest_id, keyword, priority) VALUES
    ('KW034', 'CI005', 'education', 10),
    ('KW035', 'CI005', 'teaching', 9),
    ('KW036', 'CI005', 'pedagogy', 8)
ON CONFLICT (interest_id, keyword) DO NOTHING;

-- Insert keywords for Arts & Humanities
INSERT INTO career_interest_keyword (keyword_id, interest_id, keyword, priority) VALUES
    ('KW037', 'CI006', 'arts', 9),
    ('KW038', 'CI006', 'humanities', 9),
    ('KW039', 'CI006', 'history', 8),
    ('KW040', 'CI006', 'literature', 8),
    ('KW041', 'CI006', 'philosophy', 8),
    ('KW042', 'CI006', 'classics', 7)
ON CONFLICT (interest_id, keyword) DO NOTHING;

-- Insert keywords for Sciences
INSERT INTO career_interest_keyword (keyword_id, interest_id, keyword, priority) VALUES
    ('KW043', 'CI007', 'science', 8),
    ('KW044', 'CI007', 'physics', 9),
    ('KW045', 'CI007', 'chemistry', 9),
    ('KW046', 'CI007', 'biology', 9),
    ('KW047', 'CI007', 'mathematics', 8),
    ('KW048', 'CI007', 'maths', 8),
    ('KW049', 'CI007', 'chemical', 7),
    ('KW050', 'CI007', 'biological', 7)
ON CONFLICT (interest_id, keyword) DO NOTHING;

-- Insert keywords for Social Sciences
INSERT INTO career_interest_keyword (keyword_id, interest_id, keyword, priority) VALUES
    ('KW051', 'CI008', 'sociology', 9),
    ('KW052', 'CI008', 'psychology', 9),
    ('KW053', 'CI008', 'politics', 8),
    ('KW054', 'CI008', 'international relations', 8),
    ('KW055', 'CI008', 'anthropology', 7)
ON CONFLICT (interest_id, keyword) DO NOTHING;

-- Insert keywords for Creative Arts
INSERT INTO career_interest_keyword (keyword_id, interest_id, keyword, priority) VALUES
    ('KW056', 'CI009', 'art', 9),
    ('KW057', 'CI009', 'design', 9),
    ('KW058', 'CI009', 'creative', 8),
    ('KW059', 'CI009', 'fine art', 8),
    ('KW060', 'CI009', 'graphic design', 7),
    ('KW061', 'CI009', 'fashion', 7)
ON CONFLICT (interest_id, keyword) DO NOTHING;

-- Insert keywords for Sports & Fitness
INSERT INTO career_interest_keyword (keyword_id, interest_id, keyword, priority) VALUES
    ('KW062', 'CI010', 'sports', 9),
    ('KW063', 'CI010', 'fitness', 9),
    ('KW064', 'CI010', 'exercise', 8),
    ('KW065', 'CI010', 'physical education', 8),
    ('KW066', 'CI010', 'kinesiology', 7)
ON CONFLICT (interest_id, keyword) DO NOTHING;

-- Insert conflicts: Business & Finance conflicts with Engineering & Technology, Sciences, Medicine & Healthcare
INSERT INTO career_interest_conflict (conflict_id, interest_id, conflicting_interest_id, conflict_strength) VALUES
    ('CF001', 'CI001', 'CI003', 'strong'),
    ('CF002', 'CI001', 'CI007', 'strong'),
    ('CF003', 'CI001', 'CI002', 'strong'),
    ('CF004', 'CI002', 'CI003', 'strong'),
    ('CF005', 'CI002', 'CI007', 'strong'),
    ('CF006', 'CI002', 'CI001', 'strong'),
    ('CF007', 'CI003', 'CI001', 'strong'),
    ('CF008', 'CI003', 'CI002', 'strong'),
    ('CF009', 'CI003', 'CI004', 'medium'),
    ('CF010', 'CI003', 'CI006', 'medium'),
    ('CF011', 'CI007', 'CI001', 'strong'),
    ('CF012', 'CI007', 'CI004', 'medium'),
    ('CF013', 'CI007', 'CI006', 'medium'),
    ('CF014', 'CI007', 'CI009', 'medium'),
    ('CF015', 'CI004', 'CI003', 'medium'),
    ('CF016', 'CI004', 'CI007', 'medium'),
    ('CF017', 'CI004', 'CI002', 'medium'),
    ('CF018', 'CI006', 'CI003', 'medium'),
    ('CF019', 'CI006', 'CI007', 'medium'),
    ('CF020', 'CI006', 'CI002', 'medium'),
    ('CF021', 'CI008', 'CI003', 'medium'),
    ('CF022', 'CI008', 'CI007', 'medium'),
    ('CF023', 'CI008', 'CI002', 'medium'),
    ('CF024', 'CI009', 'CI003', 'medium'),
    ('CF025', 'CI009', 'CI007', 'medium'),
    ('CF026', 'CI009', 'CI002', 'medium'),
    ('CF027', 'CI005', 'CI003', 'medium'),
    ('CF028', 'CI005', 'CI007', 'medium'),
    ('CF029', 'CI005', 'CI002', 'medium'),
    ('CF030', 'CI010', 'CI003', 'medium'),
    ('CF031', 'CI010', 'CI007', 'medium'),
    ('CF032', 'CI010', 'CI001', 'medium')
ON CONFLICT (interest_id, conflicting_interest_id) DO NOTHING;
