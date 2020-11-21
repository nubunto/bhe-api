from database import database

class PspMetrics:

  def __init__(self, database):
    self.database = database

  async def avg_wait_time(self, value):
    data = await database.fetch_one("""
            SELECT avg(desatracacao_efetiva - atracacao_efetiva) as avg
            FROM estadia
            WHERE finalidade_embarcacao = :purpose
                  and (desatracacao_efetiva - atracacao_efetiva) > interval '1 hour'
    """, {'purpose': value})
    avg = data.get('avg')
    return dict(
      days = avg.days,
      hours = avg.seconds / 60 / 60
    )

  async def avg_wait_time_by_ship_purpose(self):

    data = await database.fetch_all("""
    select avg(desatracacao_efetiva - atracacao_efetiva) avg, finalidade_embarcacao
    from estadia 
    where (desatracacao_efetiva - atracacao_efetiva) > interval '1 hour'
    group by finalidade_embarcacao
    order by avg desc;
    """)
    
    avg_time_list = [dict(days = entry.get('avg').days, hours = entry.get('avg').seconds / 60 / 60, purpose = entry.get('finalidade_embarcacao')) for entry in data]

    return avg_time_list

  async def avg_mooring_time_late(self):

    data = await database.fetch_all("""
    select avg(atracacao_efetiva - atracacao_prevista) avg, finalidade_embarcacao
    from estadia
    group by finalidade_embarcacao
    having avg(atracacao_efetiva - atracacao_prevista) > interval '0'
    order by avg desc;
    """)

    avg_time_list = [dict(days = entry.get('avg').days, hours = entry.get('avg').seconds / 60 / 60, purpose = entry.get('finalidade_embarcacao')) for entry in data]

    return avg_time_list

  async def avg_unmooring_time_late(self):

    data = await database.fetch_all("""
    select avg(desatracacao_efetiva - desatracacao_prevista) avg, finalidade_embarcacao
    from estadia
    group by finalidade_embarcacao
    having avg(desatracacao_efetiva - desatracacao_prevista) > interval '0'
    order by avg desc;
    """)

    avg_time_list = [dict(days = entry.get('avg').days,hours = entry.get('avg').seconds / 60 / 60, purpose = entry.get('finalidade_embarcacao')) for entry in data]

    return avg_time_list

  async def moorings_per_month_in_year(self, year):
    data = await database.fetch_all("""
      SELECT
        DATE_PART('month', atracacao_efetiva) as month,
        count(*) as count
      FROM estadia
      WHERE
        DATE_PART('year', atracacao_efetiva) = :year
        AND finalidade_embarcacao in (
          'Transporte de Granel Sólido',
          'Transporte de Granel Líquido'
        )
      GROUP BY month
    """, values={'year': year})

    count_list = [dict(month = entry.get('month'), count = entry.get('count')) for entry in data]

    return count_list