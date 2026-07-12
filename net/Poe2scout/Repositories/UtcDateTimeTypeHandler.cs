using System.Data;
using Dapper;

namespace Poe2scout.Repositories;

public sealed class UtcDateTimeTypeHandler : SqlMapper.TypeHandler<DateTime>
{
  public override DateTime Parse(object value)
  {
    if (value is not DateTime dateTime)
    {
      throw new DataException($"Cannot convert {value.GetType().Name} to DateTime.");
    }

    return dateTime.Kind == DateTimeKind.Utc
      ? dateTime
      : DateTime.SpecifyKind(dateTime, DateTimeKind.Utc);
  }

  public override void SetValue(IDbDataParameter parameter, DateTime value)
  {
    var utcValue = value.Kind switch
    {
      DateTimeKind.Utc => value,
      DateTimeKind.Local => value.ToUniversalTime(),
      DateTimeKind.Unspecified => DateTime.SpecifyKind(value, DateTimeKind.Utc),
      _ => throw new ArgumentOutOfRangeException(nameof(value))
    };

    parameter.DbType = DbType.DateTime2;
    parameter.Value = DateTime.SpecifyKind(utcValue, DateTimeKind.Unspecified);
  }
}
