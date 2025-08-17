using Microsoft.AspNetCore.Mvc;
using Poe2scout.Database.Models;

namespace Poe2scout.Controllers;

public partial class ItemsController
{
    [HttpGet]
    [Route("Currency")]
    public async Task<IEnumerable<GetCurrencyResponse>> GetCurrency()
    {
        return (await itemRepository.GetCurrencyItems())
            .Select(i => new GetCurrencyResponse(i));
    }
    
    public record GetCurrencyResponse(
        string ApiId,
        string Text,
        string CurrencyCategoryApiId,
        string? IconUrl,
        string ItemMetadata,
        string ItemName,
        int ItemId)
    {
        public GetCurrencyResponse(CurrencyItem ci): this(
            ApiId: ci.ApiId,
            Text: ci.Text,
            CurrencyCategoryApiId: ci.CurrencyCategoryApiId,
            IconUrl: ci.IconUrl,
            ItemMetadata: ci.ItemMetaData,
            ItemName: ci.Item.Name,
            ItemId: ci.Item.ItemId){}
    }
}
