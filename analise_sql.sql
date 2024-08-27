-- 1. Quantos chamados foram abertos no dia 01/04/2023?
SELECT 
    COUNT(c.id_chamado) 
FROM datario.adm_central_atendimento_1746.chamado c
WHERE DATE(data_inicio) = '2023-04-01'

-- 2. Qual o tipo de chamado que teve mais teve chamados abertos no dia 01/04/2023?
SELECT 
    c.tipo,
    COUNT(c.tipo) AS tipo_count
FROM datario.adm_central_atendimento_1746.chamado c
WHERE DATE(data_inicio) = '2023-04-01'
GROUP BY c.tipo
ORDER BY tipo_count DESC
LIMIT 1

-- 3. Quais os nomes dos 3 bairros que mais tiveram chamados abertos nesse dia?
SELECT 
	b.nome as bairro,
	COUNT(b.nome) as bairro_count 
FROM datario.adm_central_atendimento_1746.chamado c LEFT JOIN datario.dados_mestres.bairro b on (c.id_bairro = b.id_bairro)
WHERE DATE(data_inicio) = '2023-04-01'
GROUP BY b.nome 
ORDER BY bairro_count DESC
LIMIT 3

-- 4. Qual o nome da subprefeitura com mais chamados abertos nesse dia?
SELECT 
	b.subprefeitura,
	COUNT(b.subprefeitura) as subprefeitura_count 
FROM datario.adm_central_atendimento_1746.chamado c LEFT JOIN datario.dados_mestres.bairro b on (c.id_bairro = b.id_bairro)
WHERE DATE(data_inicio) = '2023-04-01'
GROUP BY b.subprefeitura
ORDER BY subprefeitura_count DESC
LIMIT 1

-- 5. Existe algum chamado aberto nesse dia que não foi associado a um bairro ou subprefeitura na tabela de bairros? Se sim, por que isso acontece?
SELECT 
	count(*) 
FROM datario.adm_central_atendimento_1746.chamado c LEFT JOIN datario.dados_mestres.bairro b on (c.id_bairro = b.id_bairro)
WHERE DATE(data_inicio) = '2023-04-01'
AND b.nome IS NULL

-- 6. Quantos chamados com o subtipo "Perturbação do sossego" foram abertos desde 01/01/2022 até 31/12/2023 (incluindo extremidades)?
SELECT 
	count(*) 
FROM datario.adm_central_atendimento_1746.chamado c LEFT JOIN datario.dados_mestres.bairro b on (c.id_bairro = b.id_bairro)
WHERE DATE(c.data_inicio) >= '2022-01-01' 
	AND DATE(c.data_inicio) < '2024-01-01'
	AND c.subtipo = 'Perturbação do sossego'

-- 7. Selecione os chamados com esse subtipo que foram abertos durante os eventos contidos na tabela de eventos (Reveillon, Carnaval e Rock in Rio).
SELECT
	count(*)
FROM datario.adm_central_atendimento_1746.chamado c JOIN datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos o ON DATE(c.data_inicio) BETWEEN o.data_inicial AND o.data_final
WHERE c.subtipo = 'Perturbação do sossego'

-- 8. Quantos chamados desse subtipo foram abertos em cada evento?
SELECT 
    o.evento, 
    COUNT(c.id_chamado) AS total_chamados
FROM datario.adm_central_atendimento_1746.chamado c JOIN datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos o ON DATE(c.data_inicio) BETWEEN o.data_inicial AND o.data_final
WHERE  c.subtipo = 'Perturbação do sossego'
GROUP BY o.evento;

-- 9. Qual evento teve a maior média diária de chamados abertos desse subtipo?
SELECT 
    evento,
    AVG(total_chamados) AS media_diaria_chamados
FROM 
    (SELECT 
        o.evento,
        DATE(c.data_inicio) AS dia,
        COUNT(c.id_chamado) AS total_chamados
    FROM datario.adm_central_atendimento_1746.chamado c JOIN datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos o ON DATE(c.data_inicio) BETWEEN o.data_inicial AND o.data_final
    WHERE c.subtipo = 'Perturbação do sossego'
    GROUP BY o.evento, DATE(c.data_inicio)) AS subquery
GROUP BY evento;

-- 10. **Compare as médias diárias de chamados abertos desse subtipo durante os eventos específicos (Reveillon, Carnaval e Rock in Rio) 
-- e a média diária de chamados abertos desse subtipo considerando todo o período de 01/01/2022 até 31/12/2023.**
WITH daily_counts AS (
    SELECT 
        DATE(c.data_inicio) AS dia,
        COUNT(c.id_chamado) AS total_chamados
    FROM datario.adm_central_atendimento_1746.chamado c
    WHERE c.subtipo = 'Perturbação do sossego'
    AND DATE(c.data_inicio) BETWEEN '2022-01-01' AND '2023-12-31'
    GROUP BY DATE(c.data_inicio)
)
SELECT AVG(total_chamados) AS media_diaria_chamados
FROM daily_counts;
