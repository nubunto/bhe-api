from database import database

class PspMetrics:

  def __init__(self, database):
    self.database = database

  def avg_wait_time(self, values):
    return await self.database.execute("""
            SELECT avg(desatracacao_efetiva - atracacao_efetiva)
            FROM estadia
            WHERE finalidade_embarcacao = :purpose
                  and (desatracacao_efetiva - atracacao_efetiva) > interval '1 hour'
    """, values=values)

    def avg_wait_time_by_ship_purpose():
        return await self.database.execute("""
        select avg(desatracacao_efetiva - atracacao_efetiva) abg, finalidade_embarcacao
        from estadia 
        where (desatracacao_efetiva - atracacao_efetiva) > interval '1 hour'
        group by finalidade_embarcacao
        order by abg desc;
        """)
