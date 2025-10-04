--
-- PostgreSQL database dump
--

\restrict 2wIq4zAPv5G8fdR3Ezq0iR0iucJOK8t1VCJqK5A9mnHwBPJmGGGAcfo4IvfM6au

-- Dumped from database version 17.6 (Homebrew)
-- Dumped by pg_dump version 17.6 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: refresh_leaderboard(); Type: FUNCTION; Schema: public; Owner: airees
--

CREATE FUNCTION public.refresh_leaderboard() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    REFRESH MATERIALIZED VIEW leaderboard;
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.refresh_leaderboard() OWNER TO airees;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: airees
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO airees;

--
-- Name: update_user_stats(); Type: FUNCTION; Schema: public; Owner: airees
--

CREATE FUNCTION public.update_user_stats() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    user_avg_score NUMERIC;
    user_skill_level VARCHAR(20);
BEGIN
    -- Calculate average score and determine skill level
    SELECT 
        CASE WHEN COUNT(*) = 0 THEN 0 ELSE ROUND(AVG(total_score)::NUMERIC, 2) END,
        CASE 
            WHEN COUNT(*) < 3 THEN 'beginner'
            WHEN COUNT(*) >= 5 AND AVG(total_score) >= 85 THEN 'advanced'
            WHEN COUNT(*) >= 3 AND AVG(total_score) >= 70 THEN 'intermediate'
            ELSE 'beginner'
        END
    INTO user_avg_score, user_skill_level
    FROM user_progress 
    WHERE user_id = NEW.user_id AND ldap_id = NEW.ldap_id;
    
    -- Update the current progress entry with computed skill level
    UPDATE user_progress 
    SET skill_level = user_skill_level
    WHERE id = NEW.id;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_user_stats() OWNER TO airees;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: user_badges; Type: TABLE; Schema: public; Owner: airees
--

CREATE TABLE public.user_badges (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    badge_name character varying(100) NOT NULL,
    awarded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    scenario_id character varying(10)
);


ALTER TABLE public.user_badges OWNER TO airees;

--
-- Name: user_progress; Type: TABLE; Schema: public; Owner: airees
--

CREATE TABLE public.user_progress (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    ldap_id character varying(50) NOT NULL,
    attempt_number integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    scenario_id character varying(10) NOT NULL,
    user_prompt text,
    total_score integer DEFAULT 0 NOT NULL,
    clarity_score integer DEFAULT 0 NOT NULL,
    specificity_score integer DEFAULT 0 NOT NULL,
    structure_score integer DEFAULT 0 NOT NULL,
    task_alignment_score integer DEFAULT 0 NOT NULL,
    skill_level character varying(20) DEFAULT 'beginner'::character varying NOT NULL,
    feedback text,
    strengths text[],
    improvements text[],
    session_id character varying(100),
    CONSTRAINT valid_scenario_id CHECK (((scenario_id)::text ~ '^[abi]\d+$'::text)),
    CONSTRAINT valid_scores CHECK (((total_score >= 0) AND (total_score <= 100) AND (clarity_score >= 0) AND (clarity_score <= 25) AND (specificity_score >= 0) AND (specificity_score <= 25) AND (structure_score >= 0) AND (structure_score <= 25) AND (task_alignment_score >= 0) AND (task_alignment_score <= 25) AND (total_score = (((clarity_score + specificity_score) + structure_score) + task_alignment_score)))),
    CONSTRAINT valid_skill_level CHECK (((skill_level)::text = ANY ((ARRAY['beginner'::character varying, 'intermediate'::character varying, 'advanced'::character varying])::text[])))
);


ALTER TABLE public.user_progress OWNER TO airees;

--
-- Name: users; Type: TABLE; Schema: public; Owner: airees
--

CREATE TABLE public.users (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    ldap_id character varying(50) NOT NULL,
    username character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    email_address character varying(255) NOT NULL,
    user_group character varying(100),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    last_login timestamp with time zone,
    is_active boolean DEFAULT true
);


ALTER TABLE public.users OWNER TO airees;

--
-- Name: leaderboard; Type: MATERIALIZED VIEW; Schema: public; Owner: airees
--

CREATE MATERIALIZED VIEW public.leaderboard AS
 SELECT u.ldap_id,
    u.username,
    u.user_group,
    count(up.id) AS total_attempts,
        CASE
            WHEN (count(up.id) = 0) THEN (0)::numeric
            ELSE round(avg(up.total_score), 2)
        END AS avg_score,
    max((up.skill_level)::text) AS current_skill_level,
    count(ub.id) AS total_badges,
    max(up."timestamp") AS last_activity,
    array_agg(DISTINCT ub.badge_name ORDER BY ub.badge_name) FILTER (WHERE (ub.badge_name IS NOT NULL)) AS badges
   FROM ((public.users u
     LEFT JOIN public.user_progress up ON ((u.id = up.user_id)))
     LEFT JOIN public.user_badges ub ON (((u.id = ub.user_id) AND (ub.badge_name IS NOT NULL))))
  WHERE (u.is_active = true)
  GROUP BY u.id, u.ldap_id, u.username, u.user_group
  ORDER BY
        CASE
            WHEN (count(up.id) = 0) THEN (0)::numeric
            ELSE round(avg(up.total_score), 2)
        END DESC, (count(up.id)) DESC
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.leaderboard OWNER TO airees;

--
-- Name: scenario_performance; Type: VIEW; Schema: public; Owner: airees
--

CREATE VIEW public.scenario_performance AS
 SELECT scenario_id,
    count(*) AS total_attempts,
    round(avg(total_score), 2) AS avg_score,
    min(total_score) AS min_score,
    max(total_score) AS max_score,
    round(stddev(total_score), 2) AS score_stddev,
    count(DISTINCT user_id) AS unique_users,
    round(avg(clarity_score), 2) AS avg_clarity,
    round(avg(specificity_score), 2) AS avg_specificity,
    round(avg(structure_score), 2) AS avg_structure,
    round(avg(task_alignment_score), 2) AS avg_task_alignment
   FROM public.user_progress
  GROUP BY scenario_id
  ORDER BY (round(avg(total_score), 2)) DESC;


ALTER VIEW public.scenario_performance OWNER TO airees;

--
-- Name: user_summary; Type: VIEW; Schema: public; Owner: airees
--

CREATE VIEW public.user_summary AS
 SELECT u.id,
    u.ldap_id,
    u.username,
    u.user_group,
    u.email_address,
    u.created_at,
    u.last_login,
    count(up.id) AS total_attempts,
        CASE
            WHEN (count(up.id) = 0) THEN (0)::numeric
            ELSE round(avg(up.total_score), 2)
        END AS avg_score,
    max((up.skill_level)::text) AS current_skill_level,
    count(ub.id) AS total_badges,
    max(up."timestamp") AS last_activity
   FROM ((public.users u
     LEFT JOIN public.user_progress up ON ((u.id = up.user_id)))
     LEFT JOIN public.user_badges ub ON ((u.id = ub.user_id)))
  WHERE (u.is_active = true)
  GROUP BY u.id, u.ldap_id, u.username, u.user_group, u.email_address, u.created_at, u.last_login;


ALTER VIEW public.user_summary OWNER TO airees;

--
-- Data for Name: user_badges; Type: TABLE DATA; Schema: public; Owner: airees
--

COPY public.user_badges (id, user_id, badge_name, awarded_at, scenario_id) FROM stdin;
\.


--
-- Data for Name: user_progress; Type: TABLE DATA; Schema: public; Owner: airees
--

COPY public.user_progress (id, user_id, ldap_id, attempt_number, "timestamp", scenario_id, user_prompt, total_score, clarity_score, specificity_score, structure_score, task_alignment_score, skill_level, feedback, strengths, improvements, session_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: airees
--

COPY public.users (id, ldap_id, username, password_hash, email_address, user_group, created_at, updated_at, last_login, is_active) FROM stdin;
\.


--
-- Name: user_badges unique_user_badge; Type: CONSTRAINT; Schema: public; Owner: airees
--

ALTER TABLE ONLY public.user_badges
    ADD CONSTRAINT unique_user_badge UNIQUE (user_id, badge_name);


--
-- Name: user_badges user_badges_pkey; Type: CONSTRAINT; Schema: public; Owner: airees
--

ALTER TABLE ONLY public.user_badges
    ADD CONSTRAINT user_badges_pkey PRIMARY KEY (id);


--
-- Name: user_progress user_progress_pkey; Type: CONSTRAINT; Schema: public; Owner: airees
--

ALTER TABLE ONLY public.user_progress
    ADD CONSTRAINT user_progress_pkey PRIMARY KEY (id);


--
-- Name: users users_email_address_key; Type: CONSTRAINT; Schema: public; Owner: airees
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_address_key UNIQUE (email_address);


--
-- Name: users users_ldap_id_key; Type: CONSTRAINT; Schema: public; Owner: airees
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_ldap_id_key UNIQUE (ldap_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: airees
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: airees
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_user_badges_name; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_user_badges_name ON public.user_badges USING btree (badge_name);


--
-- Name: idx_user_badges_user_id; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_user_badges_user_id ON public.user_badges USING btree (user_id);


--
-- Name: idx_user_progress_ldap_id; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_user_progress_ldap_id ON public.user_progress USING btree (ldap_id);


--
-- Name: idx_user_progress_scenario; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_user_progress_scenario ON public.user_progress USING btree (scenario_id);


--
-- Name: idx_user_progress_score; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_user_progress_score ON public.user_progress USING btree (total_score);


--
-- Name: idx_user_progress_session; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_user_progress_session ON public.user_progress USING btree (session_id);


--
-- Name: idx_user_progress_skill_level; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_user_progress_skill_level ON public.user_progress USING btree (skill_level);


--
-- Name: idx_user_progress_timestamp; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_user_progress_timestamp ON public.user_progress USING btree ("timestamp");


--
-- Name: idx_user_progress_user_id; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_user_progress_user_id ON public.user_progress USING btree (user_id);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_users_email ON public.users USING btree (email_address);


--
-- Name: idx_users_group; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_users_group ON public.users USING btree (user_group);


--
-- Name: idx_users_ldap_id; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_users_ldap_id ON public.users USING btree (ldap_id);


--
-- Name: idx_users_username; Type: INDEX; Schema: public; Owner: airees
--

CREATE INDEX idx_users_username ON public.users USING btree (username);


--
-- Name: user_badges update_leaderboard_on_badge_change; Type: TRIGGER; Schema: public; Owner: airees
--

CREATE TRIGGER update_leaderboard_on_badge_change AFTER INSERT OR DELETE OR UPDATE ON public.user_badges FOR EACH ROW EXECUTE FUNCTION public.refresh_leaderboard();


--
-- Name: user_progress update_leaderboard_on_progress_change; Type: TRIGGER; Schema: public; Owner: airees
--

CREATE TRIGGER update_leaderboard_on_progress_change AFTER INSERT OR DELETE OR UPDATE ON public.user_progress FOR EACH ROW EXECUTE FUNCTION public.refresh_leaderboard();


--
-- Name: users update_leaderboard_on_user_change; Type: TRIGGER; Schema: public; Owner: airees
--

CREATE TRIGGER update_leaderboard_on_user_change AFTER UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.refresh_leaderboard();


--
-- Name: user_progress update_user_stats_on_progress; Type: TRIGGER; Schema: public; Owner: airees
--

CREATE TRIGGER update_user_stats_on_progress AFTER INSERT ON public.user_progress FOR EACH ROW EXECUTE FUNCTION public.update_user_stats();


--
-- Name: users update_users_updated_at; Type: TRIGGER; Schema: public; Owner: airees
--

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: user_badges user_badges_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airees
--

ALTER TABLE ONLY public.user_badges
    ADD CONSTRAINT user_badges_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_progress user_progress_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airees
--

ALTER TABLE ONLY public.user_progress
    ADD CONSTRAINT user_progress_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: leaderboard; Type: MATERIALIZED VIEW DATA; Schema: public; Owner: airees
--

REFRESH MATERIALIZED VIEW public.leaderboard;


--
-- PostgreSQL database dump complete
--

\unrestrict 2wIq4zAPv5G8fdR3Ezq0iR0iucJOK8t1VCJqK5A9mnHwBPJmGGGAcfo4IvfM6au

