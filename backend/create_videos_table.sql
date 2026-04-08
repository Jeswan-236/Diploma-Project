-- Create the videos table
CREATE TABLE IF NOT EXISTS videos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    url TEXT NOT NULL,
    keywords TEXT,
    category TEXT,
    thumbnail_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert sample data from the frontend
INSERT INTO videos (title, description, url, keywords, category) VALUES
('HTML Video Class', 'Tags, structure, forms and semantic HTML.', 'https://www.youtube.com/results?search_query=html+crash+course', 'html,tags,structure,forms,semantic', 'coding'),
('CSS Video Class', 'Selectors, box model, Flexbox & Grid.', 'https://www.youtube.com/results?search_query=css+fundamentals+flexbox+grid', 'css,selectors,box model,flexbox,grid', 'coding'),
('JavaScript Video Class', 'JS basics, DOM, events and async.', 'https://www.youtube.com/results?search_query=javascript+basics+dom+events', 'javascript,dom,events,async', 'coding'),
('Python Video Class', 'Python fundamentals, data structures and examples.', 'https://www.youtube.com/results?search_query=python+for+beginners+full+course', 'python,fundamentals,data structures', 'coding'),
('MySQL Video Class', 'MySQL fundamentals, Schema, CRUD.', 'https://www.youtube.com/results?search_query=mysql+fundamentals+schema+crud', 'mysql,schema,crud', 'coding'),
('Algebra Basics', 'Foundational algebra lessons.', 'https://youtu.be/gOK4p5bBmcQ?si=QdwDgueNrYEDizXo', 'algebra,quadratic,linear,polynomials,matrix,matrices', 'maths'),
('Geometry Concepts', 'Shapes, theorems, and practice.', 'https://youtu.be/DsAuX8ExDZc?si=uQvP28n6ixK_-viA', 'geometry,triangles,circles,theorems', 'maths'),
('Calculus Intro', 'Limits, derivatives, integrals.', 'https://youtu.be/UukVP7Mg3TU?si=JAYkUwnw5I2H633a', 'calculus,limits,derivatives,integrals', 'maths'),
('Differentiation Basics', 'Rules of differentiation and practical examples.', 'https://youtu.be/6jk7ZBdEkmI?si=l7zJoXpqbqQMe_O-', 'differentiation,derivative,derivatives,rate of change', 'maths'),
('Integration & Applications', 'Indefinite and definite integrals, and applications.', 'https://youtu.be/9MqmP2QH4WA?si=uAihAPUJ45LSlaVT', 'integration,integrals,antiderivative,area under curve', 'maths'),
('Matrices & Determinants', 'Matrix operations, determinants, and solving systems.', 'https://www.youtube.com/live/6IcdcnhPGH0?si=8UzDetxNID56KWdL', 'matrix,matrices,determinant,row operations,linear algebra', 'maths'),
('Linear Algebra Basics', 'Vectors, vector spaces and core linear algebra concepts.', 'https://youtu.be/fNk_zzaMoSs?si=N35Cd8PDTASzJAH5', 'linear algebra,vectors,spaces,eigenvalues', 'maths'),
('Physics Basics', 'Mechanics and core principles.', 'https://youtu.be/aD58U3Ib0ng?si=XtySZccuRbGM6iCt', 'physics,mechanics,motion,forces', 'science'),
('Chemistry Fundamentals', 'Atoms, reactions, and practice.', 'https://youtu.be/5iTOphGnCtg?si=gbTxv4Fa3RirGvZK', 'chemistry,atoms,reactions,periodic', 'science'),
('Biology Overview', 'Cells, systems, and basics.', 'https://youtu.be/URUJD5NEXC8?si=Eli07qvPUYJMMtj2', 'biology,cells,systems,ecology', 'science')
ON CONFLICT DO NOTHING;

-- Create the ai_video_content table for AI learning feature
CREATE TABLE IF NOT EXISTS ai_video_content (
    video_id TEXT PRIMARY KEY,
    transcript_raw TEXT,
    summarized_segments JSONB,
    master_knowledge_base TEXT
);