using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Repositories.Item;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Realms;

public static class GetFiltersHandler
{
  public static async Task<Results<Ok<GetFiltersResponse>, BadRequest<string>>> GetFilters(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] IItemRepository itemRepository,
    [FromRoute] string realm)
  {
    var validatedRealm = await realmRepository.GetRealm(realm);
    if (validatedRealm is null)
    {
      return TypedResults.BadRequest("Invalid realm.");
    }

    var filters = await itemRepository.GetSearchOptions(validatedRealm.GameId);

    return TypedResults.Ok(new GetFiltersResponse(filters));
  }

  public record GetFiltersResponse(IEnumerable<GetFiltersResponse.SearchOption> Filters)
  {
    public GetFiltersResponse(IReadOnlyList<Repositories.Item.Models.SearchOption> filters) : this(
      filters.Select(filter => new SearchOption(filter))) {}

    public record SearchOption(
      string DisplayName,
      string Category,
      string Identifier,
      string ItemKind)
    {
      public SearchOption(Repositories.Item.Models.SearchOption model) : this(
        model.DisplayName,
        model.Category,
        model.Identifier,
        model.ItemKind) {}
    }
  }
}
