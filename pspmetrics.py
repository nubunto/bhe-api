from database import database

class PspMetrics:

  def __init__(self, database):
    self.database = database

  def __calculate_hours_from_timedelta(self, dt):
    return dt.seconds / 60 / 60

  async def avg_wait_time_in_days(self, value):
    data = await database.fetch_one("""
      SELECT avg(desatracacao_efetiva - atracacao_efetiva) as avg
      FROM estadia
      WHERE
        finalidade_embarcacao = :purpose
        AND (desatracacao_efetiva - atracacao_efetiva) > interval '1 hour'
    """, {'purpose': value})
    avg = data.get('avg')

    if avg == None:
      return 0
    
    return avg.days

  async def avg_wait_time_by_ship_purpose(self):

    data = await database.fetch_all("""
      SELECT
        AVG(desatracacao_efetiva - atracacao_efetiva) avg,
        finalidade_embarcacao
      FROM estadia
      WHERE (desatracacao_efetiva - atracacao_efetiva) > interval '1 hour'
            AND finalidade_embarcacao IN (
              'Transporte de Granel Sólido',
              'Transporte de Granel Líquido'
            )
      GROUP BY finalidade_embarcacao
      ORDER BY avg DESC;
    """)

    avg_time_list = [
      dict(
        days = entry.get('avg').days,
        hours = self.__calculate_hours_from_timedelta(entry.get('avg')),
        purpose = entry.get('finalidade_embarcacao')
      )
      for entry in data
    ]

    return avg_time_list

  async def avg_mooring_time_late(self):

    data = await database.fetch_all("""
    SELECT
      AVG(atracacao_efetiva - atracacao_prevista) avg,
      finalidade_embarcacao
    FROM estadia
    WHERE finalidade_embarcacao IN (
        'Transporte de Granel Sólido',
        'Transporte de Granel Líquido'
    )
    GROUP BY finalidade_embarcacao
    HAVING AVG(atracacao_efetiva - atracacao_prevista) > interval '0'
    ORDER BY avg DESC;
    """)

    avg_time_list = [dict(days = entry.get('avg').days, hours = entry.get('avg').seconds / 60 / 60, purpose = entry.get('finalidade_embarcacao')) for entry in data]

    return avg_time_list

  async def avg_unmooring_time_late(self):

    data = await database.fetch_all("""
      SELECT
        AVG(desatracacao_efetiva - desatracacao_prevista) avg,
        finalidade_embarcacao
      FROM estadia
      WHERE finalidade_embarcacao IN (
        'Transporte de Granel Sólido',
        'Transporte de Granel Líquido'
      )
      GROUP BY finalidade_embarcacao
      HAVING AVG(desatracacao_efetiva - desatracacao_prevista) > interval '0'
      ORDER BY avg DESC;
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
