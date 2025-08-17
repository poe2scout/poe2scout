using Microsoft.AspNetCore.Mvc;
using Poe2scout.Database.Models;

namespace Poe2scout.Controllers;


public partial class ItemsController
{
    [HttpGet]
    [Route("Categories")]
    public async Task<IEnumerable<GetItemCategoriesResponse>> GetItemCategories()
    {
        return (await itemRepository.GetItemCategories())
            .Select(ic => new GetItemCategoriesResponse(ic));
    }

    public record GetItemCategoriesResponse(int ItemCategoryId, string ApiId, string Label)
    {
        public GetItemCategoriesResponse(ItemCategory i) : this(
            ItemCategoryId: i.ItemCategoryId,
            ApiId: i.ApiId,
            Label: i.Label)
        {}
    }
}