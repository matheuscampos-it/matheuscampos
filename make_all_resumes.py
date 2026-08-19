import cairo
import sys
import os

class PDFResumeBuilder:
    def __init__(self, filename, title_role, accent_color=(0.1, 0.45, 0.91)):
        self.filename = filename
        self.title_role = title_role
        self.accent_color = accent_color # RGB tuple
        
        # A4 Dimensions in points: 595.27 x 841.89
        self.width = 595.27
        self.height = 841.89
        self.margin_x = 42
        self.margin_y = 38
        self.content_width = self.width - 2 * self.margin_x
        
        self.surface = cairo.PDFSurface(filename, self.width, self.height)
        self.ctx = cairo.Context(self.surface)
        self.y = self.margin_y
        self.page_num = 1

    def check_page_space(self, required_space):
        if self.y + required_space > self.height - self.margin_y:
            self.draw_footer()
            self.surface.show_page()
            self.page_num += 1
            self.y = self.margin_y
            self.draw_subsequent_header()

    def draw_footer(self):
        self.ctx.save()
        self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.ctx.set_font_size(8)
        self.ctx.set_source_rgb(0.5, 0.55, 0.6)
        page_str = f"Matheus Campos — {self.title_role} | Página {self.page_num}"
        self.ctx.move_to(self.margin_x, self.height - 20)
        self.ctx.show_text(page_str)
        self.ctx.restore()

    def draw_subsequent_header(self):
        self.ctx.save()
        self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        self.ctx.set_font_size(9.5)
        self.ctx.set_source_rgb(*self.accent_color)
        self.ctx.move_to(self.margin_x, self.y)
        self.ctx.show_text(f"MATHEUS CAMPOS — {self.title_role.upper()}")
        self.y += 14
        self.ctx.set_source_rgb(0.85, 0.88, 0.92)
        self.ctx.set_line_width(0.75)
        self.ctx.move_to(self.margin_x, self.y)
        self.ctx.line_to(self.width - self.margin_x, self.y)
        self.ctx.stroke()
        self.y += 14
        self.ctx.restore()

    def draw_header(self, lang="pt"):
        self.ctx.save()
        # Name
        self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        self.ctx.set_font_size(19)
        self.ctx.set_source_rgb(0.06, 0.09, 0.16) # Dark Slate
        self.ctx.move_to(self.margin_x, self.y)
        self.ctx.show_text("MATHEUS CAMPOS")
        self.y += 17

        # Role Subtitle
        self.ctx.set_font_size(10.5)
        self.ctx.set_source_rgb(*self.accent_color)
        self.ctx.move_to(self.margin_x, self.y)
        self.ctx.show_text(self.title_role)
        self.y += 15

        # Contact Info Bar
        self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.ctx.set_font_size(8.2)
        self.ctx.set_source_rgb(0.3, 0.35, 0.42)
        
        if lang == "en":
            contact_str = "Itajuba, MG - Brazil  |  campos98matheus@gmail.com  |  +55 (35) 98422-8704  |  linkedin.com/in/matheus-campos-it  |  github.com/matheuscampos-it"
        else:
            contact_str = "Itajubá, MG - Brasil  |  campos98matheus@gmail.com  |  (35) 98422-8704  |  linkedin.com/in/matheus-campos-it  |  github.com/matheuscampos-it"
        
        self.ctx.move_to(self.margin_x, self.y)
        self.ctx.show_text(contact_str)
        self.y += 11

        # Header Accent Line
        self.ctx.set_source_rgb(*self.accent_color)
        self.ctx.set_line_width(1.5)
        self.ctx.move_to(self.margin_x, self.y)
        self.ctx.line_to(self.width - self.margin_x, self.y)
        self.ctx.stroke()
        self.y += 14
        self.ctx.restore()

    def draw_section_heading(self, title):
        self.check_page_space(32)
        self.ctx.save()
        self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        self.ctx.set_font_size(10.5)
        self.ctx.set_source_rgb(0.06, 0.09, 0.16)
        self.ctx.move_to(self.margin_x, self.y)
        self.ctx.show_text(title.upper())
        self.y += 4

        # Thin divider under section heading
        self.ctx.set_source_rgb(*self.accent_color)
        self.ctx.set_line_width(1)
        self.ctx.move_to(self.margin_x, self.y)
        self.ctx.line_to(self.margin_x + 110, self.y)
        self.ctx.stroke()

        self.ctx.set_source_rgb(0.85, 0.88, 0.92)
        self.ctx.set_line_width(0.5)
        self.ctx.move_to(self.margin_x + 110, self.y)
        self.ctx.line_to(self.width - self.margin_x, self.y)
        self.ctx.stroke()

        self.y += 12
        self.ctx.restore()

    def wrap_text(self, text, font_size, font_weight=cairo.FONT_WEIGHT_NORMAL, max_w=None):
        if max_w is None:
            max_w = self.content_width
        self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, font_weight)
        self.ctx.set_font_size(font_size)
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            extents = self.ctx.text_extents(test_line)
            if extents.width <= max_w:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def draw_paragraph(self, text, font_size=8.8, line_height=11.5, color=(0.2, 0.25, 0.3), font_weight=cairo.FONT_WEIGHT_NORMAL):
        lines = self.wrap_text(text, font_size, font_weight)
        self.check_page_space(len(lines) * line_height + 3)
        
        self.ctx.save()
        self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, font_weight)
        self.ctx.set_font_size(font_size)
        self.ctx.set_source_rgb(*color)
        
        for line in lines:
            self.ctx.move_to(self.margin_x, self.y)
            self.ctx.show_text(line)
            self.y += line_height
        self.ctx.restore()
        self.y += 4

    def draw_bullet_point(self, title_bold, text_body, font_size=8.6, line_height=11.5):
        full_text = f"• {title_bold} {text_body}" if title_bold else f"• {text_body}"
        lines = self.wrap_text(full_text, font_size, cairo.FONT_WEIGHT_NORMAL, max_w=self.content_width - 10)
        self.check_page_space(len(lines) * line_height + 2)
        
        self.ctx.save()
        self.ctx.set_font_size(font_size)
        
        indent = self.margin_x + 9
        bullet_x = self.margin_x + 2
        
        self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        self.ctx.set_source_rgb(*self.accent_color)
        self.ctx.move_to(bullet_x, self.y)
        self.ctx.show_text("•")
        
        cur_y = self.y
        for i, line in enumerate(lines):
            self.ctx.move_to(indent, cur_y)
            line_clean = line.replace("• ", "")
            
            # Highlight bold title if present in line 0
            if i == 0 and title_bold and line_clean.startswith(title_bold):
                # Draw title in bold
                self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                self.ctx.set_source_rgb(0.1, 0.15, 0.22)
                self.ctx.show_text(title_bold + " ")
                
                # Draw rest of line
                w_title = self.ctx.text_extents(title_bold + " ").width
                rest_text = line_clean[len(title_bold) + 1:]
                self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                self.ctx.set_source_rgb(0.25, 0.3, 0.38)
                self.ctx.move_to(indent + w_title, cur_y)
                self.ctx.show_text(rest_text)
            else:
                self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                self.ctx.set_source_rgb(0.25, 0.3, 0.38)
                self.ctx.show_text(line_clean)
                
            cur_y += line_height
            
        self.y = cur_y + 1
        self.ctx.restore()

    def draw_experience_item(self, role, company, dates, bullets):
        self.check_page_space(45)
        self.ctx.save()
        
        # Role & Dates
        self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        self.ctx.set_font_size(9.5)
        self.ctx.set_source_rgb(0.06, 0.09, 0.16)
        self.ctx.move_to(self.margin_x, self.y)
        self.ctx.show_text(role)
        
        self.ctx.set_font_size(8.3)
        self.ctx.set_source_rgb(*self.accent_color)
        date_extents = self.ctx.text_extents(dates)
        self.ctx.move_to(self.width - self.margin_x - date_extents.width, self.y)
        self.ctx.show_text(dates)
        self.y += 12

        # Company
        self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
        self.ctx.set_font_size(8.6)
        self.ctx.set_source_rgb(0.35, 0.4, 0.48)
        self.ctx.move_to(self.margin_x, self.y)
        self.ctx.show_text(company)
        self.y += 13
        self.ctx.restore()

        # Bullets
        for b_title, b_body in bullets:
            self.draw_bullet_point(b_title, b_body)
        self.y += 5

    def draw_education_item(self, degree, institution, period, details=""):
        self.check_page_space(24)
        self.ctx.save()
        
        self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        self.ctx.set_font_size(9)
        self.ctx.set_source_rgb(0.06, 0.09, 0.16)
        self.ctx.move_to(self.margin_x, self.y)
        self.ctx.show_text(degree)
        
        self.ctx.set_font_size(8.2)
        self.ctx.set_source_rgb(*self.accent_color)
        p_extents = self.ctx.text_extents(period)
        self.ctx.move_to(self.width - self.margin_x - p_extents.width, self.y)
        self.ctx.show_text(period)
        self.y += 11.5

        self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
        self.ctx.set_font_size(8.3)
        self.ctx.set_source_rgb(0.35, 0.4, 0.48)
        self.ctx.move_to(self.margin_x, self.y)
        inst_text = f"{institution} — {details}" if details else institution
        self.ctx.show_text(inst_text)
        self.y += 12.5
        self.ctx.restore()

    def draw_skills_pills(self, skills):
        self.check_page_space(30)
        self.ctx.save()
        
        x = self.margin_x
        y = self.y
        row_h = 16.5
        
        for skill in skills:
            self.ctx.select_font_face('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            self.ctx.set_font_size(7.8)
            extents = self.ctx.text_extents(skill)
            pill_w = extents.width + 12
            
            if x + pill_w > self.width - self.margin_x:
                x = self.margin_x
                y += row_h
                if y > self.height - self.margin_y:
                    self.y = y
                    self.check_page_space(25)
                    y = self.y
                    x = self.margin_x

            # Pill Background
            self.ctx.set_source_rgba(self.accent_color[0], self.accent_color[1], self.accent_color[2], 0.11)
            self.ctx.new_sub_path()
            self.ctx.arc(x + 5, y + 5, 5, 3.14159/2, 3.14159)
            self.ctx.arc(x + 5, y + 11 - 5, 5, 3.14159, 3*3.14159/2)
            self.ctx.arc(x + pill_w - 5, y + 11 - 5, 5, 0, 3.14159/2)
            self.ctx.arc(x + pill_w - 5, y + 5, 5, 3*3.14159/2, 2*3.14159)
            self.ctx.close_path()
            self.ctx.fill()

            # Pill Text
            self.ctx.set_source_rgb(*self.accent_color)
            self.ctx.move_to(x + 6, y + 8.5)
            self.ctx.show_text(skill)

            x += pill_w + 5.5

        self.y = y + row_h + 3
        self.ctx.restore()

    def finish(self):
        self.draw_footer()
        self.surface.finish()

# ==============================================================================
# 1. RESUME IA: Curriculo_Matheus_Campos_Analista_Arquiteto_IA.pdf
# ==============================================================================
cv1 = PDFResumeBuilder(
    "Curriculo_Matheus_Campos_Analista_Arquiteto_IA.pdf",
    "Analista & Arquiteto de IA | Engenharia de Dados & LLMs",
    accent_color=(0.48, 0.22, 0.93) # Purple
)
cv1.draw_header("pt")

cv1.draw_section_heading("Resumo Profissional")
cv1.draw_paragraph(
    "Analista e Arquiteto de IA especializado na concepção, orquestração e implementação de soluções orientadas a Inteligência Artificial Gerativa (LLMs), automação de agentes inteligentes e pipelines de dados. Experiência comprovada no desenvolvimento de automações em Python consumindo APIs REST multi-tenant e modelos LLM para geração automatizada de relatórios executivos (escala de produção de 12 para 133 relatórios/mês). Selecionado como Estudante Embaixador do Google no Brasil (2026) com foco em IA (Gemini & Workspace). Pós-graduando em Governança de TI com sólida visão de conformidade e automação ética."
)

cv1.draw_section_heading("Experiência Profissional")
cv1.draw_experience_item(
    "Analista & Arquiteto de Soluções IA / Engenheiro de Dados",
    "Empresa de Tecnologia & Soluções Corporativas (Atuação em Produção)",
    "2024 — Presente",
    [
        ("Orquestração de Agentes IA & Pipelines:", "Desenvolvimento e implementação de pipelines em Python (Pandas/openpyxl) integrados a APIs REST multi-tenant e LLMs para geração automatizada de relatórios, multiplicando a capacidade de produção de 12 para 133 relatórios/mês com consistência e idempotência."),
        ("Engenharia de Prompt & Integração LLM:", "Arquitetura de prompts estruturados e consumo de modelos LLM (Gemini / OpenAI API) para sumarização de dados complexos e suporte à tomada de decisão."),
        ("Governança & Performance de Dados:", "Troubleshooting e otimização de consultas SQL em banco de dados relacional (MariaDB/PostgreSQL) em produção, garantindo alimentações de dados em milissegundos para modelos e dashboards."),
        ("Segurança & Conformidade Operacional:", "Suporte na reestruturação da governança de acessos (IAM por perfil), conformidade LGPD e hardening de perímetros corporativos.")
    ]
)

cv1.draw_experience_item(
    "Analista de TI, Dados & BI",
    "Inowatt Soluções Eletrotécnicas",
    "2023",
    [
        ("Dashboards & BI:", "Desenvolvimento de painéis em Power BI com higienização de fontes de dados heterogêneas e conciliação de informações financeiras/operacionais."),
        ("Suporte & Infraestrutura:", "Gestão da infraestrutura local de TI, suporte a usuários, manutenção de servidores de rede e automação de planilhas de aferição.")
    ]
)

cv1.draw_experience_item(
    "Estagiário de TI & Suporte de Redes",
    "Prefeitura Municipal de Piranguinho",
    "2020 — 2022",
    [
        ("Suporte Operacional:", "Atendimento de suporte técnico N1/N2, manutenção de hardware, administração de usuários e rotinas de backup de dados.")
    ]
)

cv1.draw_section_heading("Reconhecimentos & Liderança")
cv1.draw_bullet_point(
    "Google Student Ambassador no Brasil (Agosto — Dezembro / 2026):",
    "Selecionado para programa oficial de embaixadores técnicos do Google no Brasil. Imersão em IA Gerativa (Google Gemini), Workspace e disseminação de devlogs de engenharia de dados."
)

cv1.draw_section_heading("Formação Acadêmica")
cv1.draw_education_item(
    "Pós-Graduação em Governança de TI",
    "Faculdade Unyleya",
    "Previsão: Maio / 2026",
    "Especialização em Gestão de Riscos, Governança de Dados e Conformidade"
)
cv1.draw_education_item(
    "Bacharelado em Sistemas de Informação",
    "FEPI — Faculdade de Ciências Sociais Aplicadas de Itajubá",
    "Concluído em 2023",
    "Formação Superior em Desenvolvimento de Software, Banco de Dados e Engenharia"
)

cv1.draw_section_heading("Competências Técnicas & Tecnologias")
cv1.draw_skills_pills([
    "Python", "LLM Agents", "Google Gemini API", "OpenAI API", "Prompt Engineering",
    "APIs REST", "Pandas / ETL", "SQL Avançado", "PostgreSQL", "MariaDB",
    "Power BI (DAX)", "AWS (EC2/RDS)", "Docker", "n8n Low-Code", "Governança de TI", "Conformidade LGPD"
])
cv1.finish()
print("Created Curriculo_Matheus_Campos_Analista_Arquiteto_IA.pdf")


# ==============================================================================
# 2. RESUME BI: Curriculo_Matheus_Campos_Analista_BI_Negocios.pdf
# ==============================================================================
cv2 = PDFResumeBuilder(
    "Curriculo_Matheus_Campos_Analista_BI_Negocios.pdf",
    "Analista de BI & Negócios | Power BI, Analytics & Visualização",
    accent_color=(0.85, 0.47, 0.02) # Amber Gold
)
cv2.draw_header("pt")

cv2.draw_section_heading("Resumo Profissional")
cv2.draw_paragraph(
    "Analista de BI e Negócios especialista em transformar dados brutos e desestruturados em dashboards executivos de alto impacto e relatórios gerenciais interativos. Ampla experiência em Power BI (DAX avançado, Power Query e Modelagem Dimensional/Star Schema), higienização, tratamento e normalização de fontes heterogêneas. Atuação direta no suporte à tomada de decisão estratégica de lideranças, unindo governança de dados, métricas de negócio (KPIs) e clareza visual. Selecionado como Estudante Embaixador do Google no Brasil (2026). Bacharel em Sistemas de Informação e Pós-Graduando em Governança de TI."
)

cv2.draw_section_heading("Experiência Profissional")
cv2.draw_experience_item(
    "Analista de BI & Engenharia de Dados",
    "Empresa de Tecnologia & Soluções Corporativas (Atuação em Produção)",
    "2024 — Presente",
    [
        ("Dashboards & Visualização Analítica (Power BI):", "Higienização, tratamento e normalização de dados heterogêneos para construção de painéis estratégicos e dashboards interativos orientados à tomada de decisão."),
        ("Engenharia de Atributos & Métricas (DAX):", "Desenvolvimento de fórmulas e métricas complexas em DAX e ETL via Power Query para acompanhamento de KPIs operacionais e financeiros em tempo real."),
        ("Otimização de Fontes de Dados (SQL):", "Reescrita e tunning de consultas SQL em MariaDB/PostgreSQL em produção, eliminando gargalos de banco e garantindo atualização imediata dos relatórios de BI."),
        ("Automação de Relatórios em Python:", "Construção de pipelines em Python para consumo de APIs REST e geração automatizada de relatórios corporativos (escala de 12 para 133 relatórios/mês).")
    ]
)

cv2.draw_experience_item(
    "Analista de TI, Dados & BI",
    "Inowatt Soluções Eletrotécnicas",
    "2023",
    [
        ("Business Intelligence em Power BI:", "Criação de dashboards gerenciais em Power BI para acompanhamento de indicadores financeiros e operacionais com normalização de dados técnicos."),
        ("Gestão de Dados & Suporte:", "Manutenção e conciliação de bases operacionais, suporte a sistemas internos e infraestrutura local de TI.")
    ]
)

cv2.draw_experience_item(
    "Estagiário de TI",
    "Prefeitura Municipal de Piranguinho",
    "2020 — 2022",
    [
        ("Suporte & Gestão de Cadastros:", "Atendimento de suporte técnico a usuários, manutenção de redes locais, organização de bancos de dados cadastrais e rotinas de backup.")
    ]
)

cv2.draw_section_heading("Reconhecimentos & Liderança")
cv2.draw_bullet_point(
    "Google Student Ambassador no Brasil (Agosto — Dezembro / 2026):",
    "Reconhecimento oficial do Google no Brasil. Imersão prática no ecossistema Google Workspace e IA Gerativa (Gemini) com foco em produtividade executiva e liderança em dados."
)

cv2.draw_section_heading("Formação Acadêmica")
cv2.draw_education_item(
    "Pós-Graduação em Governança de TI",
    "Faculdade Unyleya",
    "Previsão: Maio / 2026",
    "Foco em Governança de Dados, Indicadores de Gestão e Segurança da Informação"
)
cv2.draw_education_item(
    "Bacharelado em Sistemas de Informação",
    "FEPI — Faculdade de Ciências Sociais Aplicadas de Itajubá",
    "Concluído em 2023",
    "Formação em Análise de Sistemas, Bancos de Dados Relacionais e Engenharia de Software"
)

cv2.draw_section_heading("Competências Técnicas & Tecnologias")
cv2.draw_skills_pills([
    "Power BI", "Linguagem DAX", "Power Query / ETL", "Modelagem Dimensional (Star Schema)",
    "Normalização de Dados", "SQL (PostgreSQL / MariaDB)", "Dashboards Executivos",
    "Python (Pandas)", "APIs REST", "Excel Avançado", "KPIs de Negócio", "AWS Cloud", "Governança de TI"
])
cv2.finish()
print("Created Curriculo_Matheus_Campos_Analista_BI_Negocios.pdf")


# ==============================================================================
# 3. RESUME DADOS: Curriculo_Matheus_Campos_Analista_Dados.pdf
# ==============================================================================
cv3 = PDFResumeBuilder(
    "Curriculo_Matheus_Campos_Analista_Dados.pdf",
    "Analista de Dados | SQL Avançado, Python & Pipelines ETL",
    accent_color=(0.1, 0.45, 0.91) # Tech Blue
)
cv3.draw_header("pt")

cv3.draw_section_heading("Resumo Profissional")
cv3.draw_paragraph(
    "Analista e Engenheiro de Dados com experiência no desenvolvimento de pipelines ETL/ELT, troubleshooting de performance em banco de dados relacional e análise exploratória de dados. Ampla vivência na otimização de consultas SQL complexas (MariaDB/PostgreSQL) em ambiente de produção de alto volume, eliminando timeouts e reduzindo o tempo de resposta para milissegundos. Habilidade comprovada na automação de dados em Python (Pandas/openpyxl), conciliação via APIs REST, visualização analítica em Power BI e práticas de governança de dados e nuvem (AWS EC2/RDS). Selecionado como Estudante Embaixador do Google no Brasil (2026)."
)

cv3.draw_section_heading("Experiência Profissional")
cv3.draw_experience_item(
    "Analista & Engenheiro de Dados",
    "Empresa de Tecnologia & Soluções Corporativas (Atuação em Produção)",
    "2024 — Presente",
    [
        ("Otimização SQL & Banco de Dados em Produção:", "Troubleshooting de performance em bancos relacionais (MariaDB/PostgreSQL) de alto volume. Reescrita de consultas SQL complexas para eliminação de full table scans e redução de resposta de timeout para milissegundos."),
        ("Pipelines de Dados & Automação em Python:", "Construção de pipelines em Python (Pandas/openpyxl) integradas a APIs REST multi-tenant para higienização e geração automatizada de relatórios (escala ampliada de 12 para 133 relatórios/mês)."),
        ("Dashboards & Analytics em Power BI:", "Construção de dashboards interativos em Power BI com linguagem DAX e Power Query para análise de métricas e suporte à tomada de decisão."),
        ("Governança em Nuvem (AWS) & SecOps:", "Diagnóstico e governança de instâncias EC2 e bancos RDS na AWS, aplicação do princípio de menor privilégio (IAM) e conformidade com a LGPD.")
    ]
)

cv3.draw_experience_item(
    "Analista de TI, Dados & BI",
    "Inowatt Soluções Eletrotécnicas",
    "2023",
    [
        ("Normalização de Dados & BI:", "Higienização e normalização de bases de dados heterogêneas, criação de relatórios gerenciais no Power BI e suporte de infraestrutura."),
        ("Automação Operacional:", "Desenvolvimento de rotinas para conciliação automatizada de planilhas técnicas e financeiras.")
    ]
)

cv3.draw_experience_item(
    "Estagiário de TI & Suporte",
    "Prefeitura Municipal de Piranguinho",
    "2020 — 2022",
    [
        ("Suporte & Gestão de Dados:", "Administração de contas de acesso, manutenção de redes locais e suporte ao banco de dados administrativo.")
    ]
)

cv3.draw_section_heading("Reconhecimentos & Liderança")
cv3.draw_bullet_point(
    "Google Student Ambassador no Brasil (Agosto — Dezembro / 2026):",
    "Selecionado oficialmente pelo Google. Imersão técnica em IA Gerativa (Gemini), ecossistema Google Workspace e devlogs de engenharia de dados."
)

cv3.draw_section_heading("Formação Acadêmica")
cv3.draw_education_item(
    "Pós-Graduação em Governança de TI",
    "Faculdade Unyleya",
    "Previsão: Maio / 2026",
    "Especialização em Governança de Dados, Segurança da Informação e Riscos"
)
cv3.draw_education_item(
    "Bacharelado em Sistemas de Informação",
    "FEPI — Faculdade de Ciências Sociais Aplicadas de Itajubá",
    "Concluído em 2023",
    "Formação em Sistemas de Banco de Dados, Algoritmos Avançados e Engenharia de Software"
)

cv3.draw_section_heading("Competências Técnicas & Tecnologias")
cv3.draw_skills_pills([
    "SQL Avançado (PostgreSQL / MariaDB)", "Otimização de Consultas (Tuning)", "Python (Pandas, openpyxl)",
    "APIs REST", "Pipelines ETL / ELT", "Power BI (DAX / Power Query)", "AWS (EC2, RDS, IAM)",
    "Docker", "n8n Low-Code", "Governança de Dados", "Linux / Shell", "Conformidade LGPD"
])
cv3.finish()
print("Created Curriculo_Matheus_Campos_Analista_Dados.pdf")


# ==============================================================================
# 4. RESUME ENGLISH: Resume_Matheus_Campos_Data_AI_Analyst.pdf
# ==============================================================================
cv4 = PDFResumeBuilder(
    "Resume_Matheus_Campos_Data_AI_Analyst.pdf",
    "Data & AI Analyst | Data Engineering & IT Governance",
    accent_color=(0.01, 0.52, 0.78) # Sky/Royal Blue
)
cv4.draw_header("en")

cv4.draw_section_heading("Professional Summary")
cv4.draw_paragraph(
    "Data & AI Analyst with a Bachelor’s degree in Information Systems and a Postgraduate Specialization in IT Governance (expected May 2026). Officially recognized as a Google Student Ambassador in Brazil (2026) focused on Generative AI (Gemini) and digital transformation. Proven track record in building automated Python data pipelines connected to multi-tenant REST APIs and LLM agents (scaling production throughput from 12 to 133 reports/month), optimizing high-volume production SQL databases (eliminating full table scans and timeouts), designing executive Power BI dashboards, and assisting in SecOps cloud governance (AWS EC2/RDS)."
)

cv4.draw_section_heading("Professional Experience")
cv4.draw_experience_item(
    "Data & AI Analyst / Data Engineer",
    "Corporate Tech & Enterprise Solutions Firm (Production Environment)",
    "2024 — Present",
    [
        ("Automated AI & Data Pipelines:", "Designed and implemented Python (Pandas/openpyxl) data pipelines integrated with multi-tenant REST APIs and LLM agents for automated report generation, scaling monthly output from 12 to 133 reports with zero downtime."),
        ("SQL Query Tuning & Production Database Performance:", "Performed performance troubleshooting and query rewriting on high-volume production MariaDB/PostgreSQL databases, eliminating full table scans and reducing timeouts to milliseconds."),
        ("Executive BI & Data Visualization:", "Cleansed, transformed, and normalized unstructured data sources to build interactive executive Power BI dashboards using advanced DAX metrics and Power Query ETL."),
        ("Cloud Governance & SecOps Support:", "Assisted in IAM access governance restructuring, endpoint hardening, and email authentication security (SPF/DKIM/DMARC) on AWS cloud environments.")
    ]
)

cv4.draw_experience_item(
    "IT, Data & BI Analyst",
    "Inowatt Soluções Eletrotécnicas",
    "2023",
    [
        ("Business Intelligence & Analytics:", "Developed executive Power BI dashboards for financial and operational tracking; normalized complex technical data sources."),
        ("IT Infrastructure & Support:", "Maintained internal network infrastructure, automated spreadsheet reconciliations, and managed database backups.")
    ]
)

cv4.draw_experience_item(
    "IT Support Intern",
    "Prefeitura Municipal de Piranguinho",
    "2020 — 2022",
    [
        ("IT Operations & Technical Support:", "Provided N1/N2 end-user support, local network maintenance, user account administration, and backup verification.")
    ]
)

cv4.draw_section_heading("Honors & Technical Leadership")
cv4.draw_bullet_point(
    "Google Student Ambassador in Brazil (August — December / 2026):",
    "Selected for an official Google tech leadership program. Hands-on immersion in Generative AI (Google Gemini), Google Workspace ecosystem, and technical community devlogs."
)

cv4.draw_section_heading("Education")
cv4.draw_education_item(
    "Postgraduate Specialization in IT Governance",
    "Unyleya University",
    "Expected: May 2026",
    "Focus on Data Governance, IT Risk Management, and Information Security"
)
cv4.draw_education_item(
    "Bachelor of Science in Information Systems",
    "FEPI — Faculty of Applied Social Sciences of Itajubá",
    "Graduated in 2023",
    "Core curriculum in Database Architecture, Software Engineering, and Data Analysis"
)

cv4.draw_section_heading("Technical Skills & Core Technologies")
cv4.draw_skills_pills([
    "Python (Pandas, openpyxl)", "LLM Agents (Gemini API, OpenAI)", "Advanced SQL (PostgreSQL, MariaDB)",
    "Query Optimization & Tuning", "APIs REST", "Power BI (DAX, Power Query)", "Data Normalization",
    "AWS (EC2, RDS, IAM)", "Docker", "n8n Low-Code", "IT Governance", "Linux / Shell"
])
cv4.finish()
print("Created Resume_Matheus_Campos_Data_AI_Analyst.pdf")

print("ALL 4 RESUMES GENERATED SUCCESSFULLY!")
