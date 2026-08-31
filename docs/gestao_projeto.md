# Gestão do Projeto — TerraSync AI

## Equipe (Grupo 59 — Turma 1TSCOA — Data Wars)

| RM | Integrante | Frente principal na Sprint 2 |
|---|---|---|
| 568756 | Felipe Bezerra Ambrosio Sette | Modelagem dimensional e persistência (Oracle) |
| 570809 | Renan Miguel Santana Oliveira da Silva (representante) | Power BI e repositório técnico |
| 571165 | Vinicius Santos Silva | Engenharia de dados e modelo analítico |
| 572355 | Vitor Santos Mol | Geração e qualidade das origens de dados |

## Metodologia

O grupo trabalha em ciclos semanais dentro de cada sprint do Challenge, com um
quadro de tarefas (backlog / to do / doing / concluído) para o acompanhamento diário
e checkpoints de alinhamento entre as frentes técnicas. O cronograma oficial, com
datas e responsáveis por entrega, está em `docs/roadmap.md`.

## O que mudou desde a Sprint 1 (resposta ao feedback do professor)

> *"A proposta aborda bem a contextualização do problema e apresenta uma solução
> > inovadora com uso de IA e centralização de dados. Entretanto, faltam informações
> > > claras sobre a arquitetura técnica detalhada, tecnologias usadas, protótipos
> > > > descritos e o roadmap de execução, o que compromete a completude da entrega para
> > > > > a sprint."*
> > > > >
> > > > > | Ponto do feedback | O que foi feito na Sprint 2 |
> > > > > |---|---|
> > > > > | Arquitetura técnica detalhada | `docs/arquitetura.md` detalha as 3 camadas, o fluxo ponta a ponta e o status real de implementação de cada componente (o que já roda vs. o que está modelado para a próxima evolução). |
> > > > > | Tecnologias usadas | Tabela dedicada em `docs/arquitetura.md` (seção 4) explicando o papel de cada tecnologia, com o código-fonte correspondente no repositório. |
> > > > > | Protótipos descritos | Os protótipos de tela da Sprint 1 (slide 11) agora têm contrapartida real: o painel Power BI (`powerbi/`) implementa os mesmos indicadores (umidade do solo, custo de irrigação, faixas de risco) sobre dados de fato. |
> > > > > | Roadmap de execução | `docs/roadmap.md` substitui o quadro Kanban genérico por um cronograma com datas, entregas e responsáveis nominais, cobrindo Sprint 1, Sprint 2 e a evolução planejada. |
> > > > >
> > > > > ## Modelo analítico — validação e limitações (transparência)
> > > > >
> > > > > O modelo de detecção de risco hídrico (`src/modelo_hidrico.py`) foi validado com uma
> > > > > divisão temporal (70% mais antigo para calibração do limiar, 30% mais recente para
> > > > > teste — nunca embaralhando os dados, para não vazar informação do futuro):
> > > > >
> > > > > - **Precisão do alerta "Alto risco": 100%** — quando o modelo emite esse alerta, ele
> > > > > -   sempre correspondeu, no conjunto de teste, a uma queda real de umidade abaixo do
> > > > > -     limiar crítico nos 3 dias seguintes.
> > > > > - - **Recall do alerta "Alto risco": 33,8%** — o modelo é conservador: prioriza não
> > > > >   -   gerar alarme falso para a equipe de campo, mesmo que isso signifique deixar de
> > > > >   -     capturar parte dos casos reais (esses casos tendem a ser sinalizados antes pelo
> > > > >   -   tier intermediário "Moderado", usado como aviso preventivo e não contabilizado
> > > > >   -     nessa métrica).
> > > > >  
> > > > >   - Essa é uma escolha de calibração consciente — descrita aqui exatamente pelas mesmas
> > > > >   - razões que motivaram o feedback da Sprint 1: clareza sobre o que foi feito e por quê,
> > > > >   - sem inflar resultados.
> > > > >  
> > > > >   - ## Riscos e mitigações
> > > > >  
> > > > >   - | Risco | Mitigação |
> > > > >   - |---|---|
> > > > >   - | Ausência de uma instância Oracle Database 23ai provisionada nesta sprint (conta de estudante) | Schema completo modelado e versionado (`sql/schema_oracle23ai.sql`), pronto para apontar o pipeline para uma instância real assim que disponível. |
> > > > >   - | Conectividade intermitente dos sensores IoT no campo | Já contemplado desde a Sprint 1: sincronização offline com reenvio posterior (campo `sincronizado_offline` no dado do sensor, presente também no MVP). |
> > > > >   - | Falsos positivos no alerta de risco gerando descrédito da equipe de campo | Calibração do modelo priorizando precisão (100%) sobre recall no tier "Alto", com um tier "Moderado" para aviso preventivo. |
> > > > >   - | Dependência de um único integrante para publicar/manter o painel Power BI | Projeto versionado como PBIP (texto, não binário) no GitHub — qualquer integrante pode abrir, editar e publicar. |
> > > > >   - 
