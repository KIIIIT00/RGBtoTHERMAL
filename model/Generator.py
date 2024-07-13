import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.utils import save_image
import itertools

# Generatorの定義
class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        # モデルの構成を定義
        self.model = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(inplace=True),
            # Add more layers as needed
        )


    def forward(self, x):
        # フォワードパスを定義
        return self.model(x)

# Discriminatorの定義
class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        # モデルの構成を定義
        self.model = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(inplace=True),
            # Add more layers as needed
        )

    def forward(self, x):
        # フォワードパスを定義
        return self.model(x)

# GeneratorとDiscriminatorのインスタンスを作成
G_A2B = Generator()
G_B2A = Generator()
D_A = Discriminator()
D_B = Discriminator()

# 最適化手法の設定
g_optimizer = optim.Adam(itertools.chain(G_A2B.parameters(), G_B2A.parameters()), lr=0.0002, betas=(0.5, 0.999))
d_optimizer = optim.Adam(itertools.chain(D_A.parameters(), D_B.parameters()), lr=0.0002, betas=(0.5, 0.999))

# 損失関数の定義
criterion_GAN = nn.MSELoss()
criterion_cycle = nn.L1Loss()

# データセットのロード
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

dataset = datasets.ImageFolder(root='./datasets/Scene1/', transform=transform)
dataloader = DataLoader(dataset, batch_size=1, shuffle=True)

# トレーニングループ
num_epochs = 200
for epoch in range(num_epochs):
    for i, (real_A, real_B) in enumerate(dataloader):
        # 入力テンソルをfloat型に変換
        real_A = real_A.float()
        real_B = real_B.float()
        # トレーニングステップの実装
        # Discriminatorのトレーニング
        D_A.zero_grad()
        D_B.zero_grad()

        # 本物の画像をDiscriminatorに与える
        real_A_output = D_A(real_A)
        real_B_output = D_B(real_B)

        # 偽物の画像を生成
        fake_B = G_A2B(real_A)
        fake_A = G_B2A(real_B)

        # 偽物の画像をDiscriminatorに与える
        fake_B_output = D_B(fake_B.detach())
        fake_A_output = D_A(fake_A.detach())

        # Discriminatorの損失を計算
        d_loss_A = criterion_GAN(real_A_output, torch.ones_like(real_A_output)) + \
           criterion_GAN(fake_A_output, torch.zeros_like(fake_A_output))
        d_loss_B = criterion_GAN(real_B_output, torch.ones_like(real_B_output)) + \
           criterion_GAN(fake_B_output, torch.zeros_like(fake_B_output))
        d_loss = (d_loss_A + d_loss_B) / 2

        # Discriminatorの重みを更新
        d_loss.backward()
        d_optimizer.step()

        # Generatorのトレーニング
        G_A2B.zero_grad()
        G_B2A.zero_grad()

        # 偽物の画像を生成
        fake_B = G_A2B(real_A)
        fake_A = G_B2A(real_B)

        # 偽物の画像をDiscriminatorに与える
        fake_B_output = D_B(fake_B)
        fake_A_output = D_A(fake_A)

        # Generatorの損失を計算
        g_loss_A2B = criterion_GAN(fake_B_output, torch.ones_like(fake_B_output))
        g_loss_B2A = criterion_GAN(fake_A_output, torch.ones_like(fake_A_output))

        # サイクルの損失を計算
        reconstructed_A = G_B2A(fake_B)
        reconstructed_B = G_A2B(fake_A)
        cycle_loss_A = criterion_cycle(reconstructed_A, real_A)
        cycle_loss_B = criterion_cycle(reconstructed_B, real_B)

        # 合計の損失
        g_loss = g_loss_A2B + g_loss_B2A + 10.0 * (cycle_loss_A + cycle_loss_B)

        # Generatorの重みを更新
        g_loss.backward()
        g_optimizer.step()

        pass

    print(f'Epoch [{epoch}/{num_epochs}] complete')
