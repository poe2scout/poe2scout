using Microsoft.AspNetCore.Mvc;
using Poe2scout.Database.Models;

namespace Poe2scout.Controllers;


public partial class ItemsController
{
    [HttpGet]
    public async Task<IEnumerable<GetItemsResponse>> Get()
    {
        return (await itemRepository.GetItems())
            .Select(i => new GetItemsResponse(i));
    }

    public record GetItemsResponse(string Name, int ItemId)
    {
        public GetItemsResponse(Item i) : this(
            Name: i.Name,
            ItemId: i.ItemId)
        {}
    }
}
