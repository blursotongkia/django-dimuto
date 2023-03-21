from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from . import contract, image, sku, mail, insurance, settlement, avocados
from rest_framework import routers
from rest_framework.authtoken import views
# our routes

router = routers.DefaultRouter()
router.register('trade-contracts', contract.ContractViewSet)
router.register('sku', sku.SKUViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('email', mail.email),
    path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
    path('avocados', avocados.AvocadosView.as_view()),
    path('avocados/generate-pdf/<str:trade_contract_no>/<str:role>', avocados.generate_pdf_report),
    path('avocados/update-results', avocados.update_results_by_trade_contract_no_and_role),
    path('avocados/<str:trade_contract_no>/<str:role>', avocados.get_results_by_trade_contract_no_and_role),
    path('images', image.ImageView.as_view()),
    path('images/update/', csrf_exempt(image.UpdateImage.as_view())),
    path('images/<str:trade_contract_no>', image.order_by_carton_no),
    path('images/<str:trade_contract_no>/<str:uploader_role>', image.get_company_name_and_role),
    path('sku/<str:trade_contract_no>', sku.get_sku_by_trade_contract_no),
    path('trade-contracts/company/<str:company>/', contract.get_trade_contracts_by_company),
    path('trade-contracts/<str:trade_contract_no>/<str:company>/', contract.get_role_by_company),
    path('trade-contracts/company/<str:trade_contract_no>/<str:company>', contract.get_trade_contract_by_id),
    path('insurance', insurance.InsuranceView.as_view()),
    path('insurance/status/<str:status>', insurance.get_insurance_by_status),
    path('insurance/<str:trade_contract_no>', insurance.check_if_insurance_exists),
    path('insurance/update-insurance-status/<str:trade_contract_no>', insurance.update_insurance_status),
    path('settlement/', settlement.SettlementView.as_view()),
    path('settlement/<str:trade_contract_no>', settlement.check_if_settlement_exists),
    path('settlement/update-claim-amount-status/<str:trade_contract_no>', settlement.update_claim_amount_and_status),
    path('settlement/status/<str:settlement_status>', settlement.get_settlement_by_status),
    path('settlement/update-settlement-status/<str:trade_contract_no>', settlement.update_settlement_status),
]
