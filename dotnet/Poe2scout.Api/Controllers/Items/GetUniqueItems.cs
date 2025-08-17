using Microsoft.AspNetCore.Mvc;
using Poe2scout.Database.Models;

namespace Poe2scout.Controllers;


public partial class ItemsController
{
    [HttpGet]
    [Route("Unique")]
    public async Task<ActionResult> GetUniqueItems()
    {
        return Ok((await itemRepository.GetUniqueItems())
            .Select(i => new GetUniqueItemsResponse(i))
            .ToList());
    }

    public record GetUniqueItemsResponse(
        string Name,
        string Text,
        string ItemMetadata,
        bool IsChanceable,
        string? IconUrl,
        string CategoryApiId,
        string ItemName,
        int ItemId)
    {
        public GetUniqueItemsResponse(UniqueItem ui): this(
            Name: ui.Name,
            Text: ui.Text,
            ItemMetadata: ui.ItemMetadata,
            IsChanceable: ui.IsChanceable,
            IconUrl: ui.IconUrl,
            CategoryApiId: ui.CategoryApiId,
            ItemName: ui.Item.Name,
            ItemId: ui.Item.ItemId){}
    }
}
