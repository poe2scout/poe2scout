using System.Data;
using Microsoft.AspNetCore.Mvc;
using Npgsql;
using Poe2scout.Database;
using Poe2scout.Database.Dapper.Repositories.Item;
using Scalar.AspNetCore;

[assembly: ApiController]
var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

builder.Services.AddControllers();
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();
builder.Services.AddLogging();

var connectionString = builder.Configuration["Api:DatabaseConnectionString"];

var dataSource = new NpgsqlDataSourceBuilder(connectionString).Build();

builder.Services.AddSingleton(dataSource);

builder.Services.AddScoped<IDbConnection>(sp =>
{
    var source = sp.GetRequiredService<NpgsqlDataSource>();
    return source.OpenConnection();
});

builder.Services.AddScoped<IItemRepository, ItemRepository>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.MapScalarApiReference();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();